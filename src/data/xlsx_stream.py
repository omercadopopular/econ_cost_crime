"""Small streaming XLSX reader for large retained official data files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterator
from xml.etree import ElementTree as ET
from zipfile import ZipFile


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN_NS, "r": DOC_REL_NS, "p": PKG_REL_NS}
CELL_RE = re.compile(r"([A-Z]+)")


@dataclass(frozen=True)
class SheetInfo:
    name: str
    path: str


def _column_number(reference: str) -> int:
    match = CELL_RE.match(reference)
    if not match:
        raise ValueError(f"Invalid XLSX cell reference: {reference}")
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - ord("A") + 1
    return value


def _shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    values: list[str] = []
    with archive.open("xl/sharedStrings.xml") as stream:
        for _event, node in ET.iterparse(stream, events=("end",)):
            if node.tag == f"{{{MAIN_NS}}}si":
                values.append("".join(part.text or "" for part in node.iter(f"{{{MAIN_NS}}}t")))
                node.clear()
    return values


def sheet_infos(path: Path) -> list[SheetInfo]:
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            node.attrib["Id"]: node.attrib["Target"]
            for node in relationships.findall(f"{{{PKG_REL_NS}}}Relationship")
        }
        result: list[SheetInfo] = []
        for node in workbook.findall("m:sheets/m:sheet", NS):
            target = targets[node.attrib[f"{{{DOC_REL_NS}}}id"]].replace("\\", "/")
            sheet_path = target.lstrip("/") if target.startswith("/xl/") else f"xl/{target.lstrip('/')}"
            result.append(SheetInfo(name=node.attrib["name"], path=sheet_path))
        return result


def iter_rows(path: Path, *, sheet_name: str | None = None) -> Iterator[list[object | None]]:
    """Yield worksheet rows without materializing the worksheet XML."""

    with ZipFile(path) as archive:
        sheets = sheet_infos(path)
        selected = sheets[0] if sheet_name is None else next(
            (sheet for sheet in sheets if sheet.name == sheet_name), None
        )
        if selected is None:
            raise ValueError(f"Sheet {sheet_name!r} not found in {path}; available: {[s.name for s in sheets]}")
        shared = _shared_strings(archive)
        with archive.open(selected.path) as stream:
            for _event, node in ET.iterparse(stream, events=("end",)):
                if node.tag != f"{{{MAIN_NS}}}row":
                    continue
                values: list[object | None] = []
                for cell in node.findall("m:c", NS):
                    column = _column_number(cell.attrib["r"])
                    while len(values) < column - 1:
                        values.append(None)
                    kind = cell.attrib.get("t")
                    raw = cell.findtext("m:v", default="", namespaces=NS)
                    if kind == "s":
                        value: object | None = shared[int(raw)] if raw else None
                    elif kind == "inlineStr":
                        value = "".join(part.text or "" for part in cell.iter(f"{{{MAIN_NS}}}t"))
                    elif kind in {"str", "e"}:
                        value = raw or None
                    elif kind == "b":
                        value = raw == "1"
                    elif raw == "":
                        value = None
                    else:
                        number = float(raw)
                        value = int(number) if number.is_integer() else number
                    values.append(value)
                yield values
                node.clear()
