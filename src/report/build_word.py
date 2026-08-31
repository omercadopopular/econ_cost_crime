"""Build an editable Word review draft from the report and appendix Markdown."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from src.report.build_report import (
    FIGURE_RE,
    FOOTNOTE_REFERENCE_RE,
    _extract_footnotes,
    _is_publication_metadata,
    _split_table_row,
    configure_edition as configure_report_edition,
)
from src.report import build_report as report_builder
from src.report.convert_appendix import EQUATION_TEX


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "report.md"
APPENDIX_SOURCE = ROOT / "docs" / "appendix.md"
OUTPUT = ROOT / "docs" / "report.docx"
BUILD_DIR = ROOT / "build" / "report"
HTML_PATH = BUILD_DIR / "report-word.html"
WORD_STAGING_DIR = BUILD_DIR / "word-staging"
STAGED_HTML_PATH = WORD_STAGING_DIR / "report-word.html"
METADATA_PATH = BUILD_DIR / "report-word-metadata.json"
POWERSHELL_BUILDER = ROOT / "src" / "report" / "word_from_html.ps1"
WORD_PREVIEW_PDF = BUILD_DIR / "report-word-preview.pdf"
EQUATION_DIR = BUILD_DIR / "word-equations"
EQUATION_TEX_PATH = EQUATION_DIR / "equations.tex"
EQUATION_PDF_PATH = EQUATION_DIR / "equations.pdf"
LANGUAGE = "pt"
AUTHOR_NAMES = "Carlos Góes, Lucas Siqueira Simões, Giulia Spiess e Bruna Santos"
PUBLISHER = "Inter-American Dialogue — Brazil Program"


def configure_edition(language: str) -> None:
    """Select parallel Portuguese or English Word inputs and outputs."""

    global SOURCE, APPENDIX_SOURCE, OUTPUT, BUILD_DIR, HTML_PATH, METADATA_PATH
    global WORD_STAGING_DIR, STAGED_HTML_PATH
    global WORD_PREVIEW_PDF, EQUATION_DIR, EQUATION_TEX_PATH, EQUATION_PDF_PATH
    global LANGUAGE, AUTHOR_NAMES
    configure_report_edition(language)
    LANGUAGE = language
    AUTHOR_NAMES = (
        "Carlos Góes, Lucas Siqueira Simões, Giulia Spiess e Bruna Santos"
        if language == "pt"
        else "Carlos Góes, Lucas Siqueira Simões, Giulia Spiess and Bruna Santos"
    )
    SOURCE = report_builder.SOURCE
    APPENDIX_SOURCE = report_builder.APPENDIX_SOURCE
    suffix = "" if language == "pt" else "-en"
    OUTPUT = ROOT / "docs" / f"report{suffix}.docx"
    BUILD_DIR = ROOT / "build" / f"report{suffix}"
    WORD_STAGING_DIR = BUILD_DIR / "word-staging"
    STAGED_HTML_PATH = WORD_STAGING_DIR / f"report{suffix}-word.html"
    HTML_PATH = BUILD_DIR / f"report{suffix}-word.html"
    METADATA_PATH = BUILD_DIR / f"report{suffix}-word-metadata.json"
    WORD_PREVIEW_PDF = BUILD_DIR / f"report{suffix}-word-preview.pdf"
    EQUATION_DIR = BUILD_DIR / "word-equations"
    EQUATION_TEX_PATH = EQUATION_DIR / "equations.tex"
    EQUATION_PDF_PATH = EQUATION_DIR / "equations.pdf"


def _plain_footnote(text: str) -> str:
    text = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", text)
    return text.replace("***", "").replace("**", "").replace("*", "")


def _inline_math_html(tex: str) -> str:
    """Render the compact inline-TeX subset used by the appendix as Word HTML."""
    rendered = html.escape(tex)
    rendered = re.sub(r"\\widehat\{([^{}]+)\}", r"\1&#770;", rendered)
    rendered = re.sub(r"\^\{([^{}]+)\}", r"<sup>\1</sup>", rendered)
    rendered = re.sub(r"_\{([^{}]+)\}", r"<sub>\1</sub>", rendered)
    rendered = re.sub(r"\^([A-Za-z0-9])", r"<sup>\1</sup>", rendered)
    rendered = re.sub(r"_([A-Za-z0-9]+)", r"<sub>\1</sub>", rendered)
    for command, symbol in {
        r"\alpha": "α",
        r"\beta": "β",
        r"\lambda": "λ",
        r"\rho": "ρ",
        r"\theta": "θ",
    }.items():
        rendered = rendered.replace(command, symbol)
    return f'<span class="math-inline">{rendered}</span>'


def _inline_html(text: str) -> str:
    tokens: dict[str, str] = {}

    def token(value: str) -> str:
        marker = f"ZZZHTMLTOKEN{len(tokens):04d}ZZZ"
        tokens[marker] = value
        return marker

    def replace_link(match: re.Match[str]) -> str:
        return token(
            f'<a href="{html.escape(match.group(2), quote=True)}">'
            f'{html.escape(match.group(1))}</a>'
        )

    def replace_math(match: re.Match[str]) -> str:
        return token(_inline_math_html(match.group(1)))

    def replace_footnote(match: re.Match[str]) -> str:
        return token(f'<span class="footnote-marker">[[FN:{html.escape(match.group(1))}]]</span>')

    text = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", replace_link, text)
    text = re.sub(r"(?<![\w$])\$([^$\n]+)\$(?!\$)", replace_math, text)
    text = FOOTNOTE_REFERENCE_RE.sub(replace_footnote, text)
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda match: token(f"<strong>{html.escape(match.group(1))}</strong>"),
        text,
    )
    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        lambda match: token(f"<em>{html.escape(match.group(1))}</em>"),
        text,
    )
    rendered = html.escape(text)
    for marker, value in tokens.items():
        rendered = rendered.replace(marker, value)
    return rendered


def _table_html(lines: list[str]) -> str:
    rows = [_split_table_row(line) for line in lines]
    if len(rows) < 2 or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        raise AssertionError(f"Malformed Markdown table near: {lines[0]}")
    columns = len(rows[0])
    if any(len(row) != columns for row in rows):
        raise AssertionError(f"Inconsistent table width near: {lines[0]}")
    output = ["<table>", "<thead><tr>"]
    output.extend(f"<th>{_inline_html(cell)}</th>" for cell in rows[0])
    output.extend(["</tr></thead>", "<tbody>"])
    for row in rows[2:]:
        output.append("<tr>")
        output.extend(f"<td>{_inline_html(cell)}</td>" for cell in row)
        output.append("</tr>")
    output.extend(["</tbody>", "</table>"])
    return "\n".join(output)


def _report_html() -> tuple[list[str], dict[str, str], int]:
    lines, footnotes = _extract_footnotes(SOURCE.read_text(encoding="utf-8").splitlines())
    output: list[str] = []
    figure_count = 0
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{_inline_html(stripped[2:])}</li>")
            continue
        if in_list:
            output.append("</ul>")
            in_list = False
        if stripped.startswith("# "):
            continue
        if _is_publication_metadata(stripped):
            continue
        figure = FIGURE_RE.match(stripped)
        if figure:
            pdf_path = (SOURCE.parent / figure.group(2)).resolve()
            png_path = pdf_path.with_suffix(".png")
            if not png_path.exists() or png_path.stat().st_size == 0:
                raise FileNotFoundError(f"Missing figure PNG for Word output: {png_path}")
            staged_png = WORD_STAGING_DIR / f"figure-{figure_count + 1:02d}-{png_path.name}"
            shutil.copyfile(png_path, staged_png)
            output.append(
                f'<div class="figure-page"><img src="{html.escape(staged_png.as_uri(), quote=True)}" '
                f'alt="Figura {html.escape(figure.group(1))}"></div>'
            )
            figure_count += 1
        elif stripped.startswith("## "):
            output.append(f"<h1>{_inline_html(stripped[3:])}</h1>")
        elif stripped.startswith("### "):
            output.append(f"<h2>{_inline_html(stripped[4:])}</h2>")
        elif stripped.startswith("> "):
            output.append(f"<blockquote>{_inline_html(stripped[2:])}</blockquote>")
        elif stripped.startswith("<!--"):
            raise AssertionError(f"Unsupported report comment: {stripped}")
        else:
            output.append(f"<p>{_inline_html(stripped)}</p>")
    if in_list:
        output.append("</ul>")
    return output, footnotes, figure_count


def _render_equation_images(equations: list[str]) -> list[Path]:
    """Typeset appendix TeX once and return one tightly cropped PNG per equation."""
    xelatex = shutil.which("xelatex")
    pdftoppm = shutil.which("pdftoppm")
    if not xelatex or not pdftoppm:
        raise RuntimeError("XeLaTeX and pdftoppm are required to typeset equations for Word")
    EQUATION_DIR.mkdir(parents=True, exist_ok=True)
    for old_image in EQUATION_DIR.glob("equation-*.png"):
        old_image.unlink()
    pages = []
    for equation in equations:
        pages.append(
            "\\begin{equationpage}\n"
            "\\begin{minipage}{17cm}\\centering\n"
            "\\[\n" + equation + "\n\\]\n"
            "\\end{minipage}\n"
            "\\end{equationpage}"
        )
    source = """\\documentclass[multi=equationpage,border=4pt]{standalone}
\\usepackage{fontspec}
\\IfFontExistsTF{Arial}{\\setmainfont{Arial}}{\\setmainfont{TeX Gyre Heros}}
\\usepackage{amsmath,amssymb}
\\newenvironment{equationpage}{}{}
\\begin{document}
""" + "\n".join(pages) + "\n\\end{document}\n"
    EQUATION_TEX_PATH.write_text(source, encoding="utf-8")
    compile_result = subprocess.run(
        [xelatex, "-interaction=nonstopmode", "-halt-on-error", EQUATION_TEX_PATH.name],
        cwd=EQUATION_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (EQUATION_DIR / "xelatex.log").write_text(
        compile_result.stdout + "\n" + compile_result.stderr, encoding="utf-8"
    )
    if compile_result.returncode != 0 or not EQUATION_PDF_PATH.exists():
        excerpt = "\n".join((compile_result.stdout + compile_result.stderr).splitlines()[-50:])
        raise RuntimeError(f"Equation typesetting failed:\n{excerpt}")
    render_result = subprocess.run(
        [pdftoppm, "-png", "-r", "240", EQUATION_PDF_PATH.name, "equation"],
        cwd=EQUATION_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if render_result.returncode != 0:
        raise RuntimeError(f"Equation rasterization failed:\n{render_result.stdout}\n{render_result.stderr}")
    images = sorted(EQUATION_DIR.glob("equation-*.png"))
    if len(images) != len(equations) or any(image.stat().st_size == 0 for image in images):
        raise AssertionError(
            f"Expected {len(equations)} nonempty equation images; found {len(images)}"
        )
    return images


def _appendix_html(equation_images: list[Path]) -> tuple[list[str], int, int]:
    lines = APPENDIX_SOURCE.read_text(encoding="utf-8").splitlines()
    output: list[str] = ['<div class="page-break"></div>']
    equation_count = 0
    table_count = 0
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if stripped == "$$":
            closing = index + 1
            equation_lines: list[str] = []
            while closing < len(lines) and lines[closing].strip() != "$$":
                equation_lines.append(lines[closing])
                closing += 1
            if closing == len(lines) or not equation_lines:
                raise AssertionError(f"Unclosed appendix equation at line {index + 1}")
            equation = "\n".join(equation_lines)
            image_path = equation_images[equation_count]
            staged_equation = WORD_STAGING_DIR / f"equation-{equation_count + 1:02d}.png"
            shutil.copyfile(image_path, staged_equation)
            output.append(
                f'<p class="equation"><img class="equation-image" '
                f'src="{html.escape(staged_equation.as_uri(), quote=True)}" '
                f'alt="Fórmula em TeX: {html.escape(equation, quote=True)}"></p>'
            )
            equation_count += 1
            index = closing + 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and re.match(r"^\|\s*:?-{3,}", lines[index + 1].strip()):
            table_lines = [lines[index]]
            index += 1
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            output.append(_table_html(table_lines))
            table_count += 1
            continue
        if stripped.startswith("# "):
            output.append(f"<h1>{_inline_html(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            output.append(f'<h2 class="component">{_inline_html(stripped[3:])}</h2>')
        elif stripped.startswith("### "):
            output.append(f"<h3>{_inline_html(stripped[4:])}</h3>")
        elif stripped.startswith("#### "):
            output.append(f"<h4>{_inline_html(stripped[5:])}</h4>")
        elif stripped.startswith("> "):
            output.append(f"<blockquote>{_inline_html(stripped[2:])}</blockquote>")
        elif stripped.startswith("- "):
            output.append(f"<ul><li>{_inline_html(stripped[2:])}</li></ul>")
        else:
            output.append(f"<p>{_inline_html(stripped)}</p>")
        index += 1
    return output, equation_count, table_count


def write_html_and_metadata() -> dict[str, int]:
    WORD_STAGING_DIR.mkdir(parents=True, exist_ok=True)
    report, footnotes, figure_count = _report_html()
    if report_builder.INCLUDE_APPENDIX:
        equations = list(EQUATION_TEX.values())
        equation_images = _render_equation_images(equations)
        appendix, equation_count, table_count = _appendix_html(equation_images)
    else:
        appendix, equation_count, table_count = [], 0, 0
    if figure_count != 18:
        raise AssertionError(f"Unexpected Word figure count: {figure_count}")
    if report_builder.INCLUDE_APPENDIX and (equation_count != len(EQUATION_TEX) or table_count != 15):
        raise AssertionError(
            f"Unexpected Word source structure: figures={figure_count}, equations={equation_count}, tables={table_count}"
        )
    title = (
        "Custos Econômicos da Criminalidade no Brasil"
        if LANGUAGE == "pt"
        else "The Economic Costs of Crime in Brazil"
    )
    draft_label = (
        "Primeira versão completa para revisão substantiva"
        if LANGUAGE == "pt"
        else "Complete first draft for substantive review"
    )
    toc_label = "Sumário" if LANGUAGE == "pt" else "Contents"
    html_language = "pt-BR" if LANGUAGE == "pt" else "en"
    document = f"""<!DOCTYPE html>
<html lang="{html_language}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
@page {{ size: A4; margin: 2.35cm; }}
body {{ font-family: Arial, sans-serif; font-size: 11pt; line-height: 1.28; color: #111; }}
.cover {{ page-break-after: always; padding-top: 7cm; border-top: 2px solid #1F4E79; }}
.cover h1 {{ font-size: 25pt; color: #111; margin-bottom: 24pt; }}
.cover p {{ font-size: 14pt; }}
.toc-page {{ page-break-after: always; }}
h1 {{ color: #1F4E79; font-size: 20pt; page-break-before: always; margin-top: 0; }}
h2 {{ font-size: 15pt; margin-top: 18pt; }}
h2.component {{ color: #1F4E79; page-break-before: always; }}
h3 {{ font-size: 12.5pt; margin-top: 16pt; }}
h4 {{ font-size: 11pt; margin-top: 13pt; }}
p {{ margin: 0 0 8pt 0; text-align: justify; }}
blockquote {{ margin: 10pt 24pt; padding: 8pt 12pt; border-left: 3px solid #1F4E79; background: #F4F7FA; }}
.figure-page {{ page-break-before: always; page-break-after: always; text-align: center; }}
.figure-page img {{ width: 100%; height: auto; }}
.page-break {{ page-break-before: always; }}
table {{ border-collapse: collapse; width: 100%; margin: 10pt 0 14pt 0; font-size: 9.5pt; }}
th, td {{ border: 1px solid #777; padding: 5pt; vertical-align: top; }}
th {{ background: #EAF0F5; font-weight: bold; }}
.equation {{ text-align: center; margin: 12pt 18pt; }}
.equation-image {{ max-width: 100%; width: auto; height: auto; }}
.math-inline {{ font-family: "Cambria Math", monospace; font-style: italic; }}
.footnote-marker {{ font-size: 8pt; vertical-align: super; }}
a {{ color: #1F4E79; }}
</style>
</head>
<body>
<div class="cover"><h1>{title}</h1><p>{AUTHOR_NAMES}</p><p style="color:#1F4E79">{PUBLISHER}</p><p>{draft_label}</p><p>2026</p></div>
<div class="toc-page"><h1>{toc_label}</h1><p>[[TOC]]</p></div>
{''.join(report)}
{''.join(appendix)}
</body></html>"""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(document, encoding="utf-8")
    STAGED_HTML_PATH.write_text(document, encoding="utf-8")
    metadata = {
        "footnotes": [
            {"marker": f"[[FN:{key}]]", "text": _plain_footnote(value)}
            for key, value in footnotes.items()
        ]
    }
    METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "figures": figure_count,
        "footnotes": len(footnotes),
        "equations": equation_count,
        "tables": table_count,
    }


def validate_docx(path: Path, expected: dict[str, int]) -> dict[str, int]:
    if not path.exists() or path.stat().st_size == 0:
        raise AssertionError(f"Missing or empty Word output: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        required = {"[Content_Types].xml", "word/document.xml", "word/styles.xml"}
        if not required.issubset(names):
            raise AssertionError(f"Word output lacks required OOXML parts: {required - names}")
        document = ET.fromstring(archive.read("word/document.xml"))
        footnotes_xml = archive.read("word/footnotes.xml") if "word/footnotes.xml" in names else b""
        media_count = sum(name.startswith("word/media/") for name in names)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    text = "\n".join(
        "".join(node.text or "" for node in paragraph.findall(".//w:t", namespace))
        for paragraph in document.findall(".//w:p", namespace)
    )
    required_texts = (
        [
            "1. Sumário executivo",
            "6. Conclusão",
            "Apêndice metodológico",
            "Gastos com segurança pública",
            "Gastos hospitalares",
            "Nota sobre 2025",
        ]
        if LANGUAGE == "pt"
        else [
            "1. Executive summary",
            "6. Conclusion",
            "Public and private security",
            "Medical and therapeutic services",
        ]
    )
    for required_text in required_texts:
        if required_text not in text:
            raise AssertionError(f"Expected text missing from Word output: {required_text}")
    if media_count < expected["figures"]:
        raise AssertionError(f"Expected at least {expected['figures']} embedded media files; found {media_count}")
    expected_media = expected["figures"] + expected["equations"]
    if media_count < expected_media:
        raise AssertionError(
            f"Expected at least {expected_media} embedded figures/equations; found {media_count}"
        )
    if expected["footnotes"] and not footnotes_xml:
        raise AssertionError("Word output does not contain native footnotes")
    diagnostics = {
        "embedded_media": media_count,
        "typeset_equations": expected["equations"],
        "footnote_part": int(bool(footnotes_xml)),
    }
    print("PASS: Word OOXML validated — " + ", ".join(f"{key}={value}" for key, value in diagnostics.items()))
    return diagnostics


def build_word() -> Path:
    expected = write_html_and_metadata()
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        raise RuntimeError("Windows PowerShell is required to automate Microsoft Word")
    command = [
        powershell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(POWERSHELL_BUILDER),
        "-HtmlPath",
        str(STAGED_HTML_PATH),
        "-OutputPath",
        str(OUTPUT),
        "-MetadataPath",
        str(METADATA_PATH),
        "-PreviewPdfPath",
        str(WORD_PREVIEW_PDF),
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    (BUILD_DIR / "word-build.log").write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"Word build failed:\n{result.stdout}\n{result.stderr}")
    validate_docx(OUTPUT, expected)
    if not WORD_PREVIEW_PDF.exists() or WORD_PREVIEW_PDF.stat().st_size == 0:
        raise AssertionError("Microsoft Word did not produce the diagnostic preview PDF")
    print(f"PASS: built Word review draft: {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
    print(f"Preview: {WORD_PREVIEW_PDF} ({WORD_PREVIEW_PDF.stat().st_size:,} bytes)")
    return OUTPUT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("pt", "en"), default="pt")
    args = parser.parse_args()
    configure_edition(args.language)
    build_word()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
