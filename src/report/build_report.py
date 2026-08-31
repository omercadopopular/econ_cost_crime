"""Compile ``docs/report.md`` into ``docs/report.pdf`` with XeLaTeX.

The converter intentionally supports only the Markdown constructs used by the
report: headings, paragraphs, block quotes, inline emphasis and links, Markdown
footnotes, and the repository's figure placeholders.  Keeping the conversion
small and explicit makes footnotes and figure insertion auditable without a
Pandoc dependency.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "report.md"
APPENDIX_SOURCE = ROOT / "docs" / "appendix.md"
OUTPUT = ROOT / "docs" / "report.pdf"
BUILD_DIR = ROOT / "build" / "report"
TEX_PATH = BUILD_DIR / "report.tex"

AUTHOR_NAMES = "Carlos Góes, Lucas Siqueira Simões, Giulia Spiess e Bruna Santos"
PUBLISHER = "Inter-American Dialogue — Brazil Program"
LANGUAGE = "pt"
TOC_LABEL = "Sumário"
DRAFT_LABEL = "Primeira versão completa para revisão substantiva"
APPENDIX_LABEL = "Apêndice metodológico"
INCLUDE_APPENDIX = True

FIGURE_RE = re.compile(
    r"^<!--\s*(?:FIGURA|FIGURE)\s+([0-9]{2}[A-D]?).*?:\s+(\.\./figs/[^ ]+\.pdf)\s*-->$"
)
FOOTNOTE_DEFINITION_RE = re.compile(r"^\[\^([^]]+)\]:\s*(.+)$")
FOOTNOTE_REFERENCE_RE = re.compile(r"\[\^([^]]+)\]")
LINK_RE = re.compile(r"\[([^]]+)\]\((https?://[^)]+)\)")


def configure_edition(language: str) -> None:
    """Select the parallel Portuguese or English publication paths and labels."""

    global SOURCE, APPENDIX_SOURCE, OUTPUT, BUILD_DIR, TEX_PATH
    global LANGUAGE, TOC_LABEL, DRAFT_LABEL, APPENDIX_LABEL, AUTHOR_NAMES, INCLUDE_APPENDIX
    if language not in {"pt", "en"}:
        raise ValueError(f"Unsupported report language: {language}")
    LANGUAGE = language
    suffix = "" if language == "pt" else "-en"
    SOURCE = ROOT / "docs" / f"report{suffix}.md"
    APPENDIX_SOURCE = ROOT / "docs" / f"appendix{suffix}.md"
    OUTPUT = ROOT / "docs" / f"report{suffix}.pdf"
    BUILD_DIR = ROOT / "build" / f"report{suffix}"
    TEX_PATH = BUILD_DIR / f"report{suffix}.tex"
    if language == "pt":
        INCLUDE_APPENDIX = True
        TOC_LABEL = "Sumário"
        DRAFT_LABEL = "Primeira versão completa para revisão substantiva"
        APPENDIX_LABEL = "Apêndice metodológico"
        AUTHOR_NAMES = "Carlos Góes, Lucas Siqueira Simões, Giulia Spiess e Bruna Santos"
    else:
        # The commissioned English deliverables are the translated report and
        # parallel figures. The long technical appendix remains a source document
        # of the Portuguese edition and is therefore not silently mixed into the
        # English publication.
        INCLUDE_APPENDIX = False
        TOC_LABEL = "Contents"
        DRAFT_LABEL = "Complete first draft for substantive review"
        APPENDIX_LABEL = "Methodological appendix"
        AUTHOR_NAMES = "Carlos Góes, Lucas Siqueira Simões, Giulia Spiess and Bruna Santos"


def _is_publication_metadata(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(("**Autores:**", "**Publicação:**", "**Authors:**", "**Published by:**"))


def _escape_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in text)


def _inline(text: str, footnotes: dict[str, str], *, allow_footnotes: bool = True) -> str:
    tokens: dict[str, str] = {}

    def token(value: str) -> str:
        marker = f"ZZZMARKER{len(tokens):04d}ZZZ"
        tokens[marker] = value
        return marker

    def replace_link(match: re.Match[str]) -> str:
        label = _inline(match.group(1), footnotes, allow_footnotes=False)
        url = match.group(2).replace("%", r"\%").replace("#", r"\#")
        return token(rf"\href{{{url}}}{{{label}}}")

    text = LINK_RE.sub(replace_link, text)

    def replace_inline_math(match: re.Match[str]) -> str:
        return token(rf"\({match.group(1)}\)")

    text = re.sub(r"(?<![\w$])\$([^$\n]+)\$(?!\$)", replace_inline_math, text)

    if allow_footnotes:
        def replace_footnote(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in footnotes:
                raise AssertionError(f"Undefined Markdown footnote: {key}")
            body = _inline(footnotes[key], footnotes, allow_footnotes=False)
            return token(rf"\footnote{{{body}}}")

        text = FOOTNOTE_REFERENCE_RE.sub(replace_footnote, text)

    def replace_bold(match: re.Match[str]) -> str:
        return token(rf"\textbf{{{_inline(match.group(1), footnotes, allow_footnotes=False)}}}")

    def replace_emphasis(match: re.Match[str]) -> str:
        return token(rf"\emph{{{_inline(match.group(1), footnotes, allow_footnotes=False)}}}")

    text = re.sub(r"\*\*([^*]+)\*\*", replace_bold, text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", replace_emphasis, text)
    rendered = _escape_latex(text)
    for marker, value in tokens.items():
        rendered = rendered.replace(marker, value)
    return rendered


def _extract_footnotes(lines: list[str]) -> tuple[list[str], dict[str, str]]:
    body: list[str] = []
    definitions: dict[str, str] = {}
    for line in lines:
        match = FOOTNOTE_DEFINITION_RE.match(line)
        if match:
            key, definition = match.groups()
            if key in definitions:
                raise AssertionError(f"Duplicate Markdown footnote definition: {key}")
            definitions[key] = definition
        else:
            body.append(line)
    references = set(FOOTNOTE_REFERENCE_RE.findall("\n".join(body)))
    missing = references - definitions.keys()
    unused = definitions.keys() - references
    if missing or unused:
        raise AssertionError(f"Footnote mismatch: undefined={sorted(missing)}, unused={sorted(unused)}")
    return body, definitions


def _figure_latex(relative_markdown_path: str) -> str:
    source_path = (SOURCE.parent / relative_markdown_path).resolve()
    if not source_path.is_relative_to(ROOT):
        raise AssertionError(f"Figure path escapes repository: {source_path}")
    if not source_path.exists() or source_path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty figure PDF: {source_path}")
    relative_build_path = source_path.relative_to(ROOT).as_posix()
    return "\n".join(
        [
            r"\clearpage",
            r"\begin{figure}[p]",
            r"\centering",
            rf"\includegraphics[width=\textwidth,height=0.87\textheight,keepaspectratio]{{../../{relative_build_path}}}",
            r"\end{figure}",
            r"\clearpage",
        ]
    )


def _split_table_row(line: str) -> list[str]:
    sentinel = "ZZZESCAPEDPIPEZZZ"
    protected = line.strip().strip("|").replace(r"\|", sentinel)
    return [cell.strip().replace(sentinel, "|") for cell in protected.split("|")]


def _table_latex(lines: list[str], footnotes: dict[str, str]) -> str:
    rows = [_split_table_row(line) for line in lines]
    if len(rows) < 2 or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        raise AssertionError(f"Malformed Markdown table near: {lines[0]}")
    columns = len(rows[0])
    if columns == 0 or any(len(row) != columns for row in rows):
        raise AssertionError(f"Inconsistent Markdown table width near: {lines[0]}")
    width = 0.94 / columns
    specification = "@{}" + "".join(rf"p{{{width:.3f}\textwidth}}" for _ in range(columns)) + "@{}"
    output = [rf"\begin{{longtable}}{{{specification}}}", r"\hline"]
    for row_index, row in enumerate([rows[0], *rows[2:]]):
        rendered = " & ".join(_inline(cell, footnotes) for cell in row)
        output.append(rendered + r" \\")
        if row_index == 0:
            output.extend([r"\hline", r"\endfirsthead", r"\hline", rendered + r" \\", r"\hline", r"\endhead"])
    output.extend([r"\hline", r"\end{longtable}"])
    return "\n".join(output)


def _preamble(title: str) -> str:
    formatted_title = _escape_latex(title)
    if LANGUAGE == "pt":
        formatted_title = formatted_title.replace(" no Brasil", r"\\[0.2em] no Brasil")
    elif " in Brazil" in title:
        formatted_title = formatted_title.replace(" in Brazil", r"\\[0.2em] in Brazil")
    author_latex = _escape_latex(AUTHOR_NAMES)
    publisher_latex = _escape_latex(PUBLISHER)
    return rf"""\documentclass[11pt,a4paper]{{article}}
\usepackage{{fontspec}}
\IfFontExistsTF{{Arial}}{{\setmainfont{{Arial}}}}{{\setmainfont{{TeX Gyre Heros}}}}
\usepackage[a4paper,margin=2.35cm]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{amsmath,amssymb}}
\usepackage{{array,longtable}}
\usepackage[table]{{xcolor}}
\usepackage{{hyperref}}
\definecolor{{reportblue}}{{HTML}}{{1F4E79}}
\hypersetup{{colorlinks=true,linkcolor=reportblue,urlcolor=reportblue,pdfauthor={{{author_latex}}},pdfsubject={{{publisher_latex}}},pdftitle={{{_escape_latex(title)}}}}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.68em}}
\setlength{{\emergencystretch}}{{3em}}
\renewcommand{{\arraystretch}}{{1.16}}
\setcounter{{tocdepth}}{{2}}
\renewcommand{{\contentsname}}{{{TOC_LABEL}}}
\newcommand{{\reportsection}}[1]{{\clearpage\section*{{\color{{reportblue}}#1}}\addcontentsline{{toc}}{{section}}{{#1}}}}
\newcommand{{\reportsubsection}}[1]{{\subsection*{{#1}}\addcontentsline{{toc}}{{subsection}}{{#1}}}}
\newcommand{{\appendixcomponent}}[1]{{\clearpage\subsection*{{\color{{reportblue}}#1}}\addcontentsline{{toc}}{{subsection}}{{#1}}}}
\newcommand{{\appendixsection}}[1]{{\subsubsection*{{#1}}\addcontentsline{{toc}}{{subsubsection}}{{#1}}}}
\newcommand{{\appendixsubsection}}[1]{{\paragraph{{#1}}}}
\begin{{document}}
\begin{{titlepage}}
\vspace*{{0.23\textheight}}
{{\color{{reportblue}}\rule{{\textwidth}}{{1.4pt}}}}\\[1.5em]
{{\fontsize{{25}}{{30}}\selectfont\bfseries {formatted_title}\par}}
\vspace{{1.3em}}
{{\large {author_latex}\par}}
\vspace{{0.55em}}
{{\large\color{{reportblue}} {publisher_latex}\par}}
\vspace{{1.1em}}
{{\normalsize {DRAFT_LABEL}\par}}
\vfill
{{\large 2026\par}}
{{\color{{reportblue}}\rule{{\textwidth}}{{1.4pt}}}}
\end{{titlepage}}
\tableofcontents
\clearpage
"""


def _render_appendix(footnotes: dict[str, str]) -> tuple[list[str], int, int]:
    if not APPENDIX_SOURCE.exists() or APPENDIX_SOURCE.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty Markdown appendix: {APPENDIX_SOURCE}")
    lines = APPENDIX_SOURCE.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
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
                raise AssertionError(f"Unclosed or empty TeX block at appendix line {index + 1}")
            output.extend([r"\[", "\n".join(equation_lines), r"\]"])
            equation_count += 1
            index = closing + 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and re.match(r"^\|\s*:?-{3,}", lines[index + 1].strip()):
            table_lines = [lines[index]]
            index += 1
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            output.append(_table_latex(table_lines, footnotes))
            table_count += 1
            continue
        if stripped.startswith("# "):
            output.extend([r"\clearpage", rf"\reportsection{{{_inline(stripped[2:], footnotes)}}}"])
        elif stripped.startswith("## "):
            output.append(rf"\appendixcomponent{{{_inline(stripped[3:], footnotes)}}}")
        elif stripped.startswith("### "):
            output.append(rf"\appendixsection{{{_inline(stripped[4:], footnotes)}}}")
        elif stripped.startswith("#### "):
            output.append(rf"\appendixsubsection{{{_inline(stripped[5:], footnotes)}}}")
        elif stripped.startswith("> "):
            output.append(rf"\begin{{quote}}\small {_inline(stripped[2:], footnotes)}\end{{quote}}")
        elif stripped.startswith("- "):
            output.append(rf"\begin{{itemize}}\item {_inline(stripped[2:], footnotes)}\end{{itemize}}")
        elif stripped.startswith("- "):
            output.append(rf"\begin{{itemize}}\item {_inline(stripped[2:], footnotes)}\end{{itemize}}")
        else:
            output.append(_inline(stripped, footnotes) + "\n")
        index += 1
    return output, equation_count, table_count


def convert_markdown() -> tuple[str, int, int, int, int]:
    text = SOURCE.read_text(encoding="utf-8")
    artifacts = re.findall(r"\{xx+\}|\bxxxx\b|\b(?:TODO|TBD|PENDING|XXX)\b", text, flags=re.IGNORECASE)
    if artifacts:
        raise AssertionError(f"Unresolved report artifacts: {sorted(set(artifacts))}")
    lines, footnotes = _extract_footnotes(text.splitlines())
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), None)
    if not title:
        raise AssertionError("The report must contain one level-one title")

    output: list[str] = [_preamble(title)]
    figure_count = 0
    paragraph_count = 0
    in_itemize = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if not in_itemize:
                output.append(r"\begin{itemize}")
                in_itemize = True
            output.append(rf"\item {_inline(stripped[2:], footnotes)}")
            continue
        if in_itemize:
            output.append(r"\end{itemize}")
            in_itemize = False
        if stripped.startswith("# "):
            continue
        if _is_publication_metadata(stripped):
            continue
        figure = FIGURE_RE.match(stripped)
        if figure:
            output.append(_figure_latex(figure.group(2)))
            figure_count += 1
        elif stripped.startswith("## "):
            output.append(rf"\reportsection{{{_inline(stripped[3:], footnotes)}}}")
        elif stripped.startswith("### "):
            output.append(rf"\reportsubsection{{{_inline(stripped[4:], footnotes)}}}")
        elif stripped.startswith("> "):
            output.append(rf"\begin{{quote}}\small {_inline(stripped[2:], footnotes)}\end{{quote}}")
        elif stripped.startswith("<!--"):
            raise AssertionError(f"Unsupported HTML comment in report: {stripped}")
        else:
            output.append(_inline(stripped, footnotes) + "\n")
            paragraph_count += 1
    if in_itemize:
        output.append(r"\end{itemize}")
    if figure_count != 18:
        raise AssertionError(f"Expected 18 figure placeholders; found {figure_count}")
    if INCLUDE_APPENDIX:
        appendix_output, equation_count, table_count = _render_appendix(footnotes)
        output.extend(appendix_output)
        if equation_count != 57 or table_count != 15:
            raise AssertionError(
                f"Unexpected rendered appendix structure: equations={equation_count}, tables={table_count}"
            )
    else:
        equation_count = 0
        table_count = 0
    output.append(r"\end{document}")
    return "\n".join(output), figure_count, len(footnotes), equation_count, table_count


def compile_report() -> Path:
    if shutil.which("xelatex") is None:
        raise RuntimeError("XeLaTeX is required but was not found on PATH")
    latex, figure_count, footnote_count, equation_count, table_count = convert_markdown()
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    TEX_PATH.write_text(latex, encoding="utf-8")
    command = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", TEX_PATH.name]
    for pass_number in (1, 2):
        result = subprocess.run(command, cwd=BUILD_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (BUILD_DIR / f"xelatex-pass-{pass_number}.log").write_text(
            result.stdout + "\n" + result.stderr, encoding="utf-8"
        )
        if result.returncode != 0:
            excerpt = "\n".join((result.stdout + result.stderr).splitlines()[-60:])
            raise RuntimeError(f"XeLaTeX pass {pass_number} failed:\n{excerpt}")
    compiled = TEX_PATH.with_suffix(".pdf")
    if not compiled.exists() or compiled.stat().st_size == 0:
        raise AssertionError("XeLaTeX did not produce a nonempty report PDF")
    temporary_output = OUTPUT.with_suffix(".pdf.tmp")
    shutil.copyfile(compiled, temporary_output)
    temporary_output.replace(OUTPUT)
    print(f"PASS: compiled {figure_count} figures and {footnote_count} Markdown footnotes")
    if INCLUDE_APPENDIX:
        print(f"PASS: incorporated appendix with {equation_count} TeX equations and {table_count} tables")
    else:
        print("PASS: English report compiled as a standalone translated publication")
    print(f"PDF: {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
    return OUTPUT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("pt", "en"), default="pt")
    args = parser.parse_args()
    configure_edition(args.language)
    compile_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
