"""Validate the parallel publication files and bilingual static website."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path

from src.site.build_site import CSV_NAMES, ENGLISH_CSV_NAMES


ROOT = Path(__file__).resolve().parents[2]
AUTHORS = ("Carlos Góes", "Lucas Siqueira Simões", "Giulia Spiess", "Bruna Santos")
PUBLISHER = "Inter-American Dialogue"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise AssertionError(f"Missing or empty publication file: {path}")


def validate_reports() -> int:
    checks = 0
    for suffix, heading in (("", "Sumário executivo"), ("-en", "Executive summary")):
        markdown = ROOT / "docs" / f"report{suffix}.md"
        pdf = ROOT / "docs" / f"report{suffix}.pdf"
        word = ROOT / "docs" / f"report{suffix}.docx"
        for path in (markdown, pdf, word):
            require_file(path)
            checks += 1
        text = markdown.read_text(encoding="utf-8")
        if heading not in text or PUBLISHER not in text or any(author not in text for author in AUTHORS):
            raise AssertionError(f"Publication metadata or main heading missing from {markdown}")
        if len(re.findall(r"<!--\s*(?:FIGURA|FIGURE)\s+[0-9]{2}[A-D]?", text)) != 18:
            raise AssertionError(f"Expected 18 figure placeholders in {markdown}")
        with zipfile.ZipFile(word) as archive:
            document = archive.read("word/document.xml").decode("utf-8")
            media = sum(name.startswith("word/media/") for name in archive.namelist())
        if PUBLISHER not in document or any(author not in document for author in AUTHORS):
            raise AssertionError(f"Word cover metadata missing from {word}")
        if media < 18:
            raise AssertionError(f"Expected at least 18 embedded figures in {word}; found {media}")
        checks += 4
    return checks


def validate_parallel_csvs() -> int:
    checks = 0
    for portuguese_name in CSV_NAMES:
        english_name = ENGLISH_CSV_NAMES[portuguese_name]
        pt_path = ROOT / "data" / "figure_data" / portuguese_name
        en_path = ROOT / "data" / "figure_data" / "en" / english_name
        with pt_path.open("r", encoding="utf-8", newline="") as stream:
            pt_rows = list(csv.DictReader(stream))
        with en_path.open("r", encoding="utf-8", newline="") as stream:
            en_rows = list(csv.DictReader(stream))
        if not pt_rows or len(pt_rows) != len(en_rows) or pt_rows[0].keys() != en_rows[0].keys():
            raise AssertionError(f"Parallel CSV structure differs: {pt_path} vs {en_path}")
        for pt_row, en_row in zip(pt_rows, en_rows):
            for field in pt_row:
                pt_value, en_value = pt_row[field], en_row[field]
                try:
                    pt_number = float(pt_value)
                    en_number = float(en_value)
                except ValueError:
                    continue
                if pt_number != en_number:
                    raise AssertionError(
                        f"Numeric translation drift in {english_name}: field={field}, {pt_number} != {en_number}"
                    )
        checks += 1
    return checks


def validate_figures() -> int:
    manifest_path = ROOT / "data" / "figure_data" / "en" / "english_figures_manifest.json"
    records = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(records) != 18:
        raise AssertionError(f"Expected 18 English figure records; found {len(records)}")
    for record in records:
        for field in ("data", "pdf", "png"):
            value = str(record[field])
            if re.match(r"^[A-Za-z]:[/\\]", value) or value.startswith(("/", "\\")):
                raise AssertionError(f"English figure manifest contains an absolute path: {value}")
            require_file(ROOT / value)
    return 18


def validate_site() -> int:
    index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "site" / "assets" / "js" / "app.js").read_text(encoding="utf-8")
    if len(re.findall(r'data-chart="fig[0-9]+[a-d]?"', index)) != 18:
        raise AssertionError("The site does not expose exactly 18 chart cards")
    if "data-language=\"pt\"" not in index or "data-language=\"en\"" not in index:
        raise AssertionError("The site language switch is incomplete")
    if "C:/Users/" in app or "C:\\Users\\" in app:
        raise AssertionError("The website contains a hard-coded local path")
    manifest_path = ROOT / "site" / "site-manifest.json"
    records = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(records) < 45:
        raise AssertionError(f"Site manifest is unexpectedly short: {len(records)} records")
    for record in records:
        path = ROOT / "site" / record["path"]
        require_file(path)
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise AssertionError(f"Site manifest mismatch: {path}")
    return len(records) + 3


def main() -> int:
    checks = validate_reports() + validate_parallel_csvs() + validate_figures() + validate_site()
    print(f"BILINGUAL PUBLICATION VALIDATION checks={checks} errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
