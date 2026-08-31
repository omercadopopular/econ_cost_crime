"""Read retained zipped IBGE shapefiles without extracting them."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Iterator
import zipfile

import shapefile


def shape_reader(path: Path) -> shapefile.Reader:
    with zipfile.ZipFile(path) as archive:
        members = {Path(name).suffix.lower(): name for name in archive.namelist()}
        missing = {".shp", ".shx", ".dbf"} - set(members)
        if missing:
            raise ValueError(f"Shapefile archive {path} is missing {sorted(missing)}.")
        return shapefile.Reader(
            shp=io.BytesIO(archive.read(members[".shp"])),
            shx=io.BytesIO(archive.read(members[".shx"])),
            dbf=io.BytesIO(archive.read(members[".dbf"])),
            encoding="latin1",
        )


def _distance_sq_to_segment(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> float:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if dx == 0.0 and dy == 0.0:
        return (point[0] - start[0]) ** 2 + (point[1] - start[1]) ** 2
    parameter = ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / (dx * dx + dy * dy)
    parameter = max(0.0, min(1.0, parameter))
    nearest = (start[0] + parameter * dx, start[1] + parameter * dy)
    return (point[0] - nearest[0]) ** 2 + (point[1] - nearest[1]) ** 2


def _simplify_open(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    if len(points) <= 2:
        return points
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    threshold = tolerance * tolerance
    while stack:
        start_index, end_index = stack.pop()
        largest = -1.0
        split = -1
        for index in range(start_index + 1, end_index):
            distance = _distance_sq_to_segment(points[index], points[start_index], points[end_index])
            if distance > largest:
                largest = distance
                split = index
        if split >= 0 and largest > threshold:
            keep.add(split)
            stack.append((start_index, split))
            stack.append((split, end_index))
    return [points[index] for index in sorted(keep)]


def _simplify_ring(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    if tolerance <= 0 or len(points) <= 5:
        return points
    core = points[:-1] if points[0] == points[-1] else points[:]
    if len(core) <= 4:
        return points
    left = min(range(len(core)), key=lambda index: (core[index][0], core[index][1]))
    right = max(range(len(core)), key=lambda index: (core[index][0], core[index][1]))
    if left > right:
        left, right = right, left
    first_chain = core[left : right + 1]
    second_chain = core[right:] + core[: left + 1]
    simplified = _simplify_open(first_chain, tolerance)[:-1] + _simplify_open(second_chain, tolerance)[:-1]
    if len(simplified) < 3:
        return points
    simplified.append(simplified[0])
    return simplified


def shape_rings(
    shape: shapefile.Shape,
    *,
    simplify_tolerance: float = 0.0,
) -> Iterator[list[tuple[float, float]]]:
    starts = list(shape.parts) + [len(shape.points)]
    for start, end in zip(starts[:-1], starts[1:]):
        ring = [(float(x), float(y)) for x, y in shape.points[start:end]]
        if len(ring) >= 3:
            yield _simplify_ring(ring, simplify_tolerance)
