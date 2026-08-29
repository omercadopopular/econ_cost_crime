"""Small, dependency-free reader for tabular data stored in XLSX files.

The project workbooks are ordinary Office Open XML archives.  Keeping the
reader in the standard library makes ``python -m src.validation.validate_data``
usable before a project environment has been bootstrapped.  This is not a
general Excel implementation: it reads cell values, cached formula results,
styles, comments, merged ranges, and workbook sheet metadata needed by the
audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterator
from xml.etree import ElementTree as ET
from zipfile import ZipFile


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
THREAD_NS = "http://schemas.microsoft.com/office/spreadsheetml/2018/threadedcomments"
NS = {"m": MAIN_NS, "r": REL_NS, "p": PKG_REL_NS, "tc": THREAD_NS}
CELL_RE = re.compile(r"^([A-Z]+)([0-9]+)$")


def column_number(label: str) -> int:
    """Convert an Excel column label to a one-based number."""

    value = 0
    for char in label:
        value = value * 26 + ord(char) - ord("A") + 1
    return value


def column_label(number: int) -> str:
    """Convert a one-based column number to an Excel column label."""

    if number < 1:
        raise ValueError("Excel column numbers start at one")
    chars: list[str] = []
    while number:
        number, remainder = divmod(number - 1, 26)
        chars.append(chr(ord("A") + remainder))
    return "".join(reversed(chars))


def split_reference(reference: str) -> tuple[int, int]:
    """Return ``(row, column)`` for an A1 cell reference."""

    match = CELL_RE.match(reference.replace("$", ""))
    if not match:
        raise ValueError(f"Unsupported Excel cell reference: {reference}")
    return int(match.group(2)), column_number(match.group(1))


@dataclass(frozen=True)
class CellStyle:
    style_id: int
    number_format_id: int
    number_format: str | None
    font_color: str | None
    fill_color: str | None


@dataclass(frozen=True)
class Cell:
    reference: str
    row: int
    column: int
    value: Any
    formula: str | None
    style: CellStyle
    comment: str | None = None


@dataclass(frozen=True)
class Sheet:
    name: str
    state: str
    path: str
    dimension: str | None
    merged_ranges: tuple[str, ...]
    cells: dict[str, Cell]

    @property
    def max_row(self) -> int:
        return max((cell.row for cell in self.cells.values()), default=0)

    @property
    def max_column(self) -> int:
        return max((cell.column for cell in self.cells.values()), default=0)

    def cell(self, row: int, column: int) -> Cell | None:
        return self.cells.get(f"{column_label(column)}{row}")

    def iter_rows(
        self,
        min_row: int = 1,
        max_row: int | None = None,
        min_column: int = 1,
        max_column: int | None = None,
    ) -> Iterator[list[Cell | None]]:
        final_row = self.max_row if max_row is None else max_row
        final_column = self.max_column if max_column is None else max_column
        for row in range(min_row, final_row + 1):
            yield [self.cell(row, column) for column in range(min_column, final_column + 1)]

    def values(self, **kwargs: int | None) -> Iterator[list[Any]]:
        for row in self.iter_rows(**kwargs):
            yield [cell.value if cell else None for cell in row]


class Workbook:
    """Read the audit-relevant subset of an XLSX workbook."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        with ZipFile(self.path) as archive:
            self._shared_strings = self._read_shared_strings(archive)
            self._styles = self._read_styles(archive)
            self.sheets = self._read_sheets(archive)
            self.calculation_properties = self._read_calculation_properties(archive)

    @staticmethod
    def _text_content(node: ET.Element) -> str:
        return "".join(part.text or "" for part in node.findall(".//m:t", NS))

    def _read_shared_strings(self, archive: ZipFile) -> list[str]:
        if "xl/sharedStrings.xml" not in archive.namelist():
            return []
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        return [self._text_content(item) for item in root.findall("m:si", NS)]

    @staticmethod
    def _color(node: ET.Element | None) -> str | None:
        if node is None:
            return None
        for attribute in ("rgb", "theme", "indexed", "auto"):
            if attribute in node.attrib:
                return f"{attribute}:{node.attrib[attribute]}"
        return None

    def _read_styles(self, archive: ZipFile) -> list[CellStyle]:
        root = ET.fromstring(archive.read("xl/styles.xml"))
        custom_formats = {
            int(node.attrib["numFmtId"]): node.attrib.get("formatCode")
            for node in root.findall("m:numFmts/m:numFmt", NS)
        }
        fonts = root.findall("m:fonts/m:font", NS)
        fills = root.findall("m:fills/m:fill", NS)
        styles: list[CellStyle] = []
        for style_id, node in enumerate(root.findall("m:cellXfs/m:xf", NS)):
            number_format_id = int(node.attrib.get("numFmtId", "0"))
            font_id = int(node.attrib.get("fontId", "0"))
            fill_id = int(node.attrib.get("fillId", "0"))
            font_color = None
            fill_color = None
            if font_id < len(fonts):
                font_color = self._color(fonts[font_id].find("m:color", NS))
            if fill_id < len(fills):
                pattern = fills[fill_id].find("m:patternFill", NS)
                if pattern is not None:
                    fill_color = self._color(pattern.find("m:fgColor", NS))
            styles.append(
                CellStyle(
                    style_id=style_id,
                    number_format_id=number_format_id,
                    number_format=custom_formats.get(number_format_id),
                    font_color=font_color,
                    fill_color=fill_color,
                )
            )
        if not styles:
            styles.append(CellStyle(0, 0, None, None, None))
        return styles

    @staticmethod
    def _relationships(archive: ZipFile, path: str) -> dict[str, tuple[str, str | None]]:
        if path not in archive.namelist():
            return {}
        root = ET.fromstring(archive.read(path))
        return {
            node.attrib["Id"]: (node.attrib["Target"], node.attrib.get("Type"))
            for node in root.findall("p:Relationship", NS)
        }

    @staticmethod
    def _resolve_target(base: str, target: str) -> str:
        if target.startswith("/"):
            return target.lstrip("/")
        parts: list[str] = []
        for part in (PurePosixPath(base).parent / target).parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        return "/".join(parts)

    def _read_comments(self, archive: ZipFile, sheet_path: str) -> dict[str, str]:
        rel_path = str(
            PurePosixPath(sheet_path).parent
            / "_rels"
            / f"{PurePosixPath(sheet_path).name}.rels"
        )
        relationships = self._relationships(archive, rel_path)
        comments_target = next(
            (
                target
                for target, rel_type in relationships.values()
                if rel_type and rel_type.endswith("/comments")
            ),
            None,
        )
        comments: dict[str, list[str]] = {}
        if comments_target is not None:
            comments_path = self._resolve_target(sheet_path, comments_target)
            root = ET.fromstring(archive.read(comments_path))
            for node in root.findall("m:commentList/m:comment", NS):
                text = self._text_content(node.find("m:text", NS) or node)
                # Excel writes a generic compatibility warning into legacy
                # comments when the substantive text lives in a threaded
                # comment.  Do not repeat that warning in audit output.
                if not text.startswith("[Threaded comment]"):
                    comments.setdefault(node.attrib["ref"], []).append(text)

        threaded_target = next(
            (
                target
                for target, rel_type in relationships.values()
                if rel_type and rel_type.endswith("/threadedComment")
            ),
            None,
        )
        if threaded_target is not None:
            threaded_path = self._resolve_target(sheet_path, threaded_target)
            root = ET.fromstring(archive.read(threaded_path))
            for node in root.findall("tc:threadedComment", NS):
                text_node = node.find("tc:text", NS)
                text = text_node.text if text_node is not None else None
                if text:
                    comments.setdefault(node.attrib["ref"], []).append(text)
        return {reference: "\n\n".join(items) for reference, items in comments.items()}

    def _parse_cell_value(self, node: ET.Element) -> Any:
        value_type = node.attrib.get("t")
        if value_type == "inlineStr":
            inline = node.find("m:is", NS)
            return self._text_content(inline) if inline is not None else ""
        value_node = node.find("m:v", NS)
        if value_node is None or value_node.text is None:
            return None
        raw = value_node.text
        if value_type == "s":
            return self._shared_strings[int(raw)]
        if value_type in {"str", "e", "d"}:
            return raw
        if value_type == "b":
            return raw == "1"
        try:
            numeric = float(raw)
        except ValueError:
            return raw
        return int(numeric) if numeric.is_integer() else numeric

    def _read_sheet(self, archive: ZipFile, name: str, state: str, path: str) -> Sheet:
        root = ET.fromstring(archive.read(path))
        comments = self._read_comments(archive, path)
        cells: dict[str, Cell] = {}
        for node in root.findall("m:sheetData/m:row/m:c", NS):
            reference = node.attrib["r"]
            row, column = split_reference(reference)
            style_id = int(node.attrib.get("s", "0"))
            formula_node = node.find("m:f", NS)
            cells[reference] = Cell(
                reference=reference,
                row=row,
                column=column,
                value=self._parse_cell_value(node),
                formula=formula_node.text if formula_node is not None else None,
                style=self._styles[style_id],
                comment=comments.get(reference),
            )
        dimension = root.find("m:dimension", NS)
        merged = tuple(
            node.attrib["ref"] for node in root.findall("m:mergeCells/m:mergeCell", NS)
        )
        return Sheet(
            name=name,
            state=state,
            path=path,
            dimension=dimension.attrib.get("ref") if dimension is not None else None,
            merged_ranges=merged,
            cells=cells,
        )

    def _read_sheets(self, archive: ZipFile) -> dict[str, Sheet]:
        workbook_path = "xl/workbook.xml"
        root = ET.fromstring(archive.read(workbook_path))
        relationships = self._relationships(archive, "xl/_rels/workbook.xml.rels")
        sheets: dict[str, Sheet] = {}
        for node in root.findall("m:sheets/m:sheet", NS):
            relationship_id = node.attrib[f"{{{REL_NS}}}id"]
            target, _ = relationships[relationship_id]
            path = self._resolve_target(workbook_path, target)
            name = node.attrib["name"]
            sheets[name] = self._read_sheet(
                archive=archive,
                name=name,
                state=node.attrib.get("state", "visible"),
                path=path,
            )
        return sheets

    @staticmethod
    def _read_calculation_properties(archive: ZipFile) -> dict[str, str]:
        root = ET.fromstring(archive.read("xl/workbook.xml"))
        node = root.find("m:calcPr", NS)
        return dict(node.attrib) if node is not None else {}
