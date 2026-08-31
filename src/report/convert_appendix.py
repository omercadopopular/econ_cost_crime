"""Convert the authoritative methodological appendix DOCX to Markdown.

The source DOCX stores equations as formatted Unicode text rather than OMML.
For that reason, every display equation is mapped explicitly to TeX below.  The
conversion fails if the source gains or loses an equation without a matching
update, preventing silent degradation of mathematical notation.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "appendix.docx"
OUTPUT = ROOT / "docs" / "appendix.md"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
W = f"{{{W_NS}}}"
R = f"{{{R_NS}}}"


EQUATION_TEX = {
    "GSPₜ = Gᵁₜ + Gᴱₜ + Gᴹₜ,": r"GSP_t = G_t^{U} + G_t^{E} + G_t^{M},",
    "GSPₜᵈᵉᶻ·²⁰²⁵ = GSPₜᵒʳⁱᵍᵉᵐ × I(bₜ → dez. 2025),": r"GSP_t^{\mathrm{dez.\,2025}} = GSP_t^{\mathrm{origem}} \times I(b_t \rightarrow \text{dez. 2025}),",
    "Mg,t = 12 × Σi∈g wi yi,": r"M_{g,t} = 12 \times \sum_{i \in g} w_i y_i,",
    "GSPt = 1,86 × MF,t + MI,t,": r"GSP_t = 1{,}86 \times M_{F,t} + M_{I,t},",
    "União líquidaₜ = União liquidada brutaₜ − transferências às UFs nas modalidades 30 e 31ₜ": r"\text{União líquida}_t = \text{União liquidada bruta}_t - \text{transferências às UFs nas modalidades 30 e 31}_t",
    "UF ausenteᵢ,ₜ = média simples dos valores reportados pelas UFs no ano t": r"\text{UF ausente}_{i,t} = \text{média simples dos valores reportados pelas UFs no ano }t",
    "ρ = Σ UFs liquidadas₂₀₁₄–₂₀₁₆ / Σ UFs empenhadas₂₀₁₄–₂₀₁₆ = 0,9638414359": r"\rho = \frac{\sum \text{UFs liquidadas}_{2014\text{--}2016}}{\sum \text{UFs empenhadas}_{2014\text{--}2016}} = 0{,}9638414359",
    "UFs liquidadas estimadasₜ = ρ × UFs empenhadasₜ, para t = 2004, …, 2010": r"\text{UFs liquidadas estimadas}_t = \rho \times \text{UFs empenhadas}_t, \quad t=2004,\ldots,2010",
    "UFsₜ = UFs₂₀₀₄ × [λ(Pₜ/P₂₀₀₄) + (1 − λ)(Wₜ/W₂₀₀₄)]": r"\mathrm{UFs}_t = \mathrm{UFs}_{2004}\left[\lambda\frac{P_t}{P_{2004}} + (1-\lambda)\frac{W_t}{W_{2004}}\right]",
    "λ̂ = arg minλ Σₜ₌₂₀₀₅²⁰⁰⁷ [Yₜ/Y₂₀₀₄ − λ(Pₜ/P₂₀₀₄) − (1 − λ)(Wₜ/W₂₀₀₄)]²": r"\widehat{\lambda}=\operatorname*{arg\,min}_{\lambda}\sum_{t=2005}^{2007}\left[\frac{Y_t}{Y_{2004}}-\lambda\frac{P_t}{P_{2004}}-(1-\lambda)\frac{W_t}{W_{2004}}\right]^2",
    "União liquidada bruta₂₀₀₀ = 142.590.083,93 − 40.104.307,75 = R$ 102.485.776,18": r"\text{União liquidada bruta}_{2000}=142{.}590{.}083{,}93-40{.}104{.}307{,}75=\text{R\$ }102{.}485{.}776{,}18",
    "θ = Σ União líquida₂₀₀₁–₂₀₀₃ / Σ União bruta₂₀₀₁–₂₀₀₃ = 0,0560114542": r"\theta=\frac{\sum \text{União líquida}_{2001\text{--}2003}}{\sum \text{União bruta}_{2001\text{--}2003}}=0{,}0560114542",
    "União líquida₂₀₀₀ = R$ 102.485.776,18 × θ = R$ 5.740.377,36": r"\text{União líquida}_{2000}=\text{R\$ }102{.}485{.}776{,}18\times\theta=\text{R\$ }5{.}740{.}377{,}36",
    "Uniãoₜ = União₂₀₀₀ × (Pₜ/P₂₀₀₀), para t = 1996, …, 1999": r"\text{União}_t=\text{União}_{2000}\times\frac{P_t}{P_{2000}},\quad t=1996,\ldots,1999",
    "P₁₉₉₆ = √(P₁₉₉₅ × P₁₉₉₇) = 159.307,1044": r"P_{1996}=\sqrt{P_{1995}\times P_{1997}}=159{.}307{,}1044",
    "P₁₉₉₈ = √(P₁₉₉₇ × P₁₉₉₉) = 181.959,9202": r"P_{1998}=\sqrt{P_{1997}\times P_{1999}}=181{.}959{,}9202",
    "Valor em dezembro de 2025ₜ = Valor nominalₜ × fator IPCAₜ→dez/2025": r"\text{Valor em dezembro de 2025}_t=\text{Valor nominal}_t\times\text{fator IPCA}_{t\rightarrow\mathrm{dez./2025}}",
    "Gasto com segurosₛ,ₜ = Σᵣ Prêmio diretoᵣ,ₜ, para todo r incluído no cenário s.": r"\text{Gasto com seguros}_{s,t}=\sum_r \text{Prêmio direto}_{r,t},\quad \forall r\in s.",
    "Sinistro híbridoₘ = sinistro diretoₘ, se damesano ≤ 201311; sinistro ocorridoₘ, se damesano ≥ 201312.": r"\text{Sinistro híbrido}_m=\begin{cases}\text{sinistro direto}_m,&\text{se damesano}\leq 201311,\\\text{sinistro ocorrido}_m,&\text{se damesano}\geq 201312.\end{cases}",
    "ln(Qₜ) = α + ln(Dₜ) + εₜ  ⇔  Q̂ₜ = exp(α̂) × Dₜ.": r"\ln(Q_t)=\alpha+\ln(D_t)+\varepsilon_t\quad\Longleftrightarrow\quad\widehat{Q}_t=\exp(\widehat{\alpha})\times D_t.",
    "Vₜ = Σₕ (Vₜ,ₕ × FREQ_SIN1ₜ,ₕ) / Σₕ FREQ_SIN1ₜ,ₕ, em que h identifica o semestre.": r"V_t=\frac{\sum_h V_{t,h}\times \mathrm{FREQ\_SIN1}_{t,h}}{\sum_h \mathrm{FREQ\_SIN1}_{t,h}},\quad\text{em que }h\text{ identifica o semestre}.",
    "Fₜ = 0,960206 × Fᵃₜ + 0,039794 × Fᵐₜ;  Vₜ = R$ 41.636,61 × Fₜ.": r"F_t=0{,}960206\times F_t^a+0{,}039794\times F_t^m;\qquad V_t=\text{R\$ }41{.}636{,}61\times F_t.",
    "Perda automotivaₜ = Qₜ × Vₜ × (1 − r) = Qₜ × Vₜ × 0,635.": r"\text{Perda automotiva}_t=Q_t\times V_t\times(1-r)=Q_t\times V_t\times0{,}635.",
    "Perdas materiaisₜ = Perda patrimonialₜ + Perda de cargaₜ + Perda automotivaₜ.": r"\text{Perdas materiais}_t=\text{Perda patrimonial}_t+\text{Perda de carga}_t+\text{Perda automotiva}_t.",
    "Total do eixoₜ = Seguros automotivosₜ + Seguros patrimoniaisₜ + Seguros de cargaₜ + Perdas patrimoniaisₜ + Perdas de cargaₜ + Perdas automotivasₜ.": r"\begin{aligned}\text{Total do eixo}_t={}&\text{Seguros automotivos}_t+\text{Seguros patrimoniais}_t+\text{Seguros de carga}_t\\&+\text{Perdas patrimoniais}_t+\text{Perdas de carga}_t+\text{Perdas automotivas}_t.\end{aligned}",
    "Valor em dez./2025ₜ = Valor nominalₜ × Deflator IPCAₜ→dez./2025.": r"\text{Valor em dez./2025}_t=\text{Valor nominal}_t\times\text{Deflator IPCA}_{t\rightarrow\mathrm{dez./2025}}.",
    "w(i,r) = E[Y(i,r) | ocupado]": r"w(i,r)=\mathbb{E}\!\left[Y(i,r)\mid\mathrm{ocupado}\right]",
    "γ(i,r) = P[ocupado(i,r) = 1]": r"\gamma(i,r)=\Pr\!\left[\mathrm{ocupado}(i,r)=1\right]",
    "RE(i,r) = w(i,r) × γ(i,r)": r"RE(i,r)=w(i,r)\times\gamma(i,r)",
    "S(i,j) = l(j) / l(i)": r"S(i,j)=\frac{l(j)}{l(i)}",
    "VP(i,r) = Σ[j = máx(i+1,14) até 90] {12 × RE(j,r) × [l(j)/l(i)] × [(1+g)^(j−i)/(1+d)^(j−i)]}": r"VP(i,r)=\sum_{j=\max(i+1,14)}^{90}12\times RE(j,r)\times\frac{l(j)}{l(i)}\times\frac{(1+g)^{j-i}}{(1+d)^{j-i}}",
    "Perda observada(t,r) = Σ[i] H(i,t,r) × VP(i,r)": r"\text{Perda observada}(t,r)=\sum_i H(i,t,r)\times VP(i,r)",
    "VP médio observado(t,r) = Perda observada(t,r) / Homicídios com idade conhecida(t,r)": r"\text{VP médio observado}(t,r)=\frac{\text{Perda observada}(t,r)}{\text{Homicídios com idade conhecida}(t,r)}",
    "Perda imputada(t,r) = Homicídios sem idade(t,r) × VP médio observado(t,r)": r"\text{Perda imputada}(t,r)=\text{Homicídios sem idade}(t,r)\times\text{VP médio observado}(t,r)",
    "Perda total(t,r) = Perda observada(t,r) + Perda imputada(t,r)": r"\text{Perda total}(t,r)=\text{Perda observada}(t,r)+\text{Perda imputada}(t,r)",
    "Perda produtiva Brasil(t) = Σ[r] Perda total(t,r)": r"\text{Perda produtiva Brasil}(t)=\sum_r\text{Perda total}(t,r)",
    "P_crim^TJ(u,t) = [SentCrim(u,t) × TempoCrim(u)] / {[SentCrim(u,t) × TempoCrim(u)] + [SentNCrim(u,t) × TempoNCrim(u)]}.": r"P_{\mathrm{crim}}^{TJ}(u,t)=\frac{\mathrm{SentCrim}(u,t)\times\mathrm{TempoCrim}(u)}{\mathrm{SentCrim}(u,t)\times\mathrm{TempoCrim}(u)+\mathrm{SentNCrim}(u,t)\times\mathrm{TempoNCrim}(u)}.",
    "G_crim^TJ(u,t) = DPJ_real(u,t) × P_crim^TJ(u,t).": r"G_{\mathrm{crim}}^{TJ}(u,t)=DPJ_{\mathrm{real}}(u,t)\times P_{\mathrm{crim}}^{TJ}(u,t).",
    "G_não_crim^TJ(u,t) = DPJ_real(u,t) × [1 − P_crim^TJ(u,t)].": r"G_{\mathrm{não\_crim}}^{TJ}(u,t)=DPJ_{\mathrm{real}}(u,t)\times\left[1-P_{\mathrm{crim}}^{TJ}(u,t)\right].",
    "ln(DPJ_real(t) / Pop(t)) = α + βt + ε(t),": r"\ln\!\left(\frac{DPJ_{\mathrm{real}}(t)}{\mathrm{Pop}(t)}\right)=\alpha+\beta t+\varepsilon(t),",
    "P_crim^MP = Volume criminal / (Volume criminal + Volume não criminal) = 0,6872.": r"P_{\mathrm{crim}}^{MP}=\frac{\text{Volume criminal}}{\text{Volume criminal}+\text{Volume não criminal}}=0{,}6872.",
    "G_crim^MP(u,t) = Despesa_real^MP(u,t) × 0,6872.": r"G_{\mathrm{crim}}^{MP}(u,t)=\mathrm{Despesa}_{\mathrm{real}}^{MP}(u,t)\times0{,}6872.",
    "Despesa_real^MP(t) = DPJ_real(t) × 0,3036929.": r"\mathrm{Despesa}_{\mathrm{real}}^{MP}(t)=DPJ_{\mathrm{real}}(t)\times0{,}3036929.",
    "ln(MP(u,t)) = ln(MP(u,a)) + [(t − a) / (b − a)] × [ln(MP(u,b)) − ln(MP(u,a))],": r"\ln MP(u,t)=\ln MP(u,a)+\frac{t-a}{b-a}\left[\ln MP(u,b)-\ln MP(u,a)\right],",
    "MP(u,t) = MP(u,2008) × [DPJ_real(u,t) / DPJ_real(u,2008)].": r"MP(u,t)=MP(u,2008)\times\frac{DPJ_{\mathrm{real}}(u,t)}{DPJ_{\mathrm{real}}(u,2008)}.",
    "G_defesa_comum(u,t) = CnCCrim1(u,t) × H_comum(u).": r"G_{\mathrm{defesa\_comum}}(u,t)=CnCCrim1(u,t)\times H_{\mathrm{comum}}(u).",
    "G_defesa_JECRIM(u,t) = CnCCrimJE(u,t) × H_JECRIM(u).": r"G_{\mathrm{defesa\_JECRIM}}(u,t)=CnCCrimJE(u,t)\times H_{\mathrm{JECRIM}}(u).",
    "G_defesa(u,t) = G_defesa_comum(u,t) + G_defesa_JECRIM(u,t).": r"G_{\mathrm{defesa}}(u,t)=G_{\mathrm{defesa\_comum}}(u,t)+G_{\mathrm{defesa\_JECRIM}}(u,t).",
    "H_médio_comum = R$ 14.150,49.": r"H_{\mathrm{médio\_comum}}=\text{R\$ }14{.}150{,}49.",
    "H_médio_JECRIM = R$ 6.212,02.": r"H_{\mathrm{médio\_JECRIM}}=\text{R\$ }6{.}212{,}02.",
    "CnCCrim1(t) = Cn1(t) × 0,1243312.": r"CnCCrim1(t)=Cn1(t)\times0{,}1243312.",
    "CnCCrimJE(t) = CnJE(t) × 0,2289453.": r"CnCCrimJE(t)=CnJE(t)\times0{,}2289453.",
    "G_justiça_criminal(t) = G_crim^TJ(t) + G_crim^MP(t) + G_defesa(t).": r"G_{\mathrm{justiça\_criminal}}(t)=G_{\mathrm{crim}}^{TJ}(t)+G_{\mathrm{crim}}^{MP}(t)+G_{\mathrm{defesa}}(t).",
    "C_SUS(t) = Σ[i ∈ A(t)] VAL_TOT(i) × F_IPCA(t).": r"C_{\mathrm{SUS}}(t)=\sum_{i\in A(t)}VAL_{\mathrm{TOT}}(i)\times F_{\mathrm{IPCA}}(t).",
    "PP_temp(i) = [RE(a(i), r(i)) / 30] × DIAS_PERM(i).": r"PP_{\mathrm{temp}}(i)=\frac{RE(a(i),r(i))}{30}\times DIAS_{\mathrm{PERM}}(i).",
    "PP_temp(t) = Σ[i ∈ A_nf(t)] PP_temp(i).": r"PP_{\mathrm{temp}}(t)=\sum_{i\in A_{\mathrm{nf}}(t)}PP_{\mathrm{temp}}(i).",
    "G_hospitalar(t) = C_SUS(t) + PP_temp(t).": r"G_{\mathrm{hospitalar}}(t)=C_{\mathrm{SUS}}(t)+PP_{\mathrm{temp}}(t).",
}


COMMENT_NOTE_AFTER = (
    "O eixo abrange exclusivamente mortes identificadas como homicídios no Sistema de Informações "
    "sobre Mortalidade (SIM/DATASUS)."
)
COMMENT_NOTE = (
    "> **Nota sobre 2025.** Na ausência de microdados regionais completos do SIM para 2025, "
    "a estimativa nacional utiliza o total agregado de homicídios de 2025 e a distribuição por idade "
    "e grande região observada em 2024, último perfil completo disponível."
)

SUBSCRIPT_MAP = str.maketrans("\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089\u208c\u2095\u2098\u209b\u209c\u1d62\u1d63", "0123456789=hmstir")
SUPERSCRIPT_MAP = {
    "²": "2", "⁰": "0", "ⁱ": "i", "⁵": "5", "⁷": "7",
    "ʳ": "r", "ᴱ": "E", "ᴹ": "M", "ᵁ": "U", "ᵃ": "a",
    "ᵈ": "d", "ᵉ": "e", "ᵍ": "g", "ᵐ": "m", "ᵒ": "o", "ᶻ": "z",
}
SUBSCRIPT_CHARS = "₀₁₂₃₄₅₆₇₈₉₌ₕₘₛₜᵢᵣ"
SUPERSCRIPT_CHARS = "".join(SUPERSCRIPT_MAP)
SCRIPT_TOKEN_RE = re.compile(
    rf"(?<![\w])([A-Za-z]+(?:[\u0302{re.escape(SUBSCRIPT_CHARS + SUPERSCRIPT_CHARS)}·]+))"
)
GREEK_INLINE = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "ε": r"\varepsilon",
    "θ": r"\theta", "λ": r"\lambda", "ρ": r"\rho",
}


def _text(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.iter(f"{W}t")).strip()


def _scripted_token_to_tex(token: str) -> str:
    result = ""
    index = 0
    while index < len(token):
        character = token[index]
        if character == "\u0302":
            result = rf"\widehat{{{result}}}"
            index += 1
        elif character in SUBSCRIPT_CHARS:
            sequence = ""
            while index < len(token) and token[index] in SUBSCRIPT_CHARS:
                sequence += token[index].translate(SUBSCRIPT_MAP)
                index += 1
            result += rf"_{{{sequence}}}"
        elif character in SUPERSCRIPT_MAP or character == "·":
            sequence = ""
            while index < len(token) and (token[index] in SUPERSCRIPT_MAP or token[index] == "·"):
                sequence += r"\," if token[index] == "·" else SUPERSCRIPT_MAP[token[index]]
                index += 1
            result += rf"^{{{sequence}}}"
        else:
            result += character
            index += 1
    return result


def _convert_inline_math(text: str) -> str:
    text = SCRIPT_TOKEN_RE.sub(lambda match: f"${_scripted_token_to_tex(match.group(1))}$", text)
    greek_pattern = re.compile(rf"(?<![\w$])([{''.join(GREEK_INLINE)}])(\u0302)?(?![\w$])")

    def replace_greek(match: re.Match[str]) -> str:
        value = GREEK_INLINE[match.group(1)]
        if match.group(2):
            value = rf"\widehat{{{value}}}"
        return f"${value}$"

    return greek_pattern.sub(replace_greek, text)


def _run_markdown(run: ET.Element) -> str:
    text = "".join(node.text or "" for node in run.iter(f"{W}t"))
    if not text:
        return ""
    props = run.find(f"./{W}rPr")
    bold = props is not None and props.find(f"./{W}b") is not None
    italic = props is not None and props.find(f"./{W}i") is not None
    if bold and italic:
        return f"***{text}***"
    if bold:
        return f"**{text}**"
    if italic:
        return f"*{text}*"
    return text


def _paragraph_markdown(paragraph: ET.Element, relationships: dict[str, str]) -> str:
    pieces: list[str] = []
    for child in paragraph:
        if child.tag == f"{W}r":
            pieces.append(_run_markdown(child))
        elif child.tag == f"{W}hyperlink":
            label = "".join(_run_markdown(run) for run in child.findall(f"./{W}r"))
            target = relationships.get(child.get(f"{R}id", ""))
            pieces.append(f"[{label}]({target})" if target else label)
    return _convert_inline_math("".join(pieces).strip())


def _paragraph_style(paragraph: ET.Element) -> str:
    style = paragraph.find(f"./{W}pPr/{W}pStyle")
    return style.get(f"{W}val", "") if style is not None else ""


def _paragraph_alignment(paragraph: ET.Element) -> str:
    alignment = paragraph.find(f"./{W}pPr/{W}jc")
    return alignment.get(f"{W}val", "") if alignment is not None else ""


def _maximum_font_size(paragraph: ET.Element) -> int:
    sizes = [int(node.get(f"{W}val")) for node in paragraph.findall(f".//{W}sz") if node.get(f"{W}val")]
    return max(sizes, default=0)


def _has_italic_run(paragraph: ET.Element) -> bool:
    return any(run.find(f"./{W}rPr/{W}i") is not None for run in paragraph.findall(f"./{W}r"))


def _is_equation(paragraph: ET.Element, text: str) -> bool:
    if not text or text.startswith("•") or len(text) >= 320 or "=" not in text:
        return False
    return _paragraph_alignment(paragraph) in {"center", "left"} or _has_italic_run(paragraph)


def _table_markdown(table: ET.Element, relationships: dict[str, str]) -> str:
    rows: list[list[str]] = []
    for row in table.findall(f"./{W}tr"):
        cells: list[str] = []
        for cell in row.findall(f"./{W}tc"):
            parts = [
                _paragraph_markdown(paragraph, relationships)
                for paragraph in cell.findall(f"./{W}p")
            ]
            value = "; ".join(part for part in parts if part).replace("|", r"\|")
            cells.append(value)
        if any(cell.strip() for cell in cells):
            rows.append(cells)
    if not rows:
        return ""
    columns = max(len(row) for row in rows)
    rows = [row + [""] * (columns - len(row)) for row in rows]
    output = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join(["---"] * columns) + " |"]
    output.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join(output)


def convert() -> dict[str, int]:
    if not SOURCE.exists() or SOURCE.stat().st_size == 0:
        raise FileNotFoundError(f"Missing appendix source: {SOURCE}")
    with zipfile.ZipFile(SOURCE) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        rels_root = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
    relationships = {
        relationship.get("Id", ""): relationship.get("Target", "")
        for relationship in rels_root.findall(f"{{{PKG_REL_NS}}}Relationship")
    }
    body = document.find(f".//{W}body")
    if body is None:
        raise AssertionError("DOCX document body is missing")

    output = [
        "# Apêndice metodológico",
        "",
        "Este apêndice documenta as fontes, as definições, as fórmulas e os tratamentos empregados na construção das séries atualizadas.",
        "",
    ]
    equations_seen: set[str] = set()
    component_count = 0
    table_count = 0
    hyperlink_count = 0
    note_added = False

    for block in body:
        if block.tag == f"{W}tbl":
            output.extend([_table_markdown(block, relationships), ""])
            table_count += 1
            continue
        if block.tag != f"{W}p":
            continue
        raw_text = _text(block)
        if not raw_text:
            continue
        hyperlink_count += len(block.findall(f".//{W}hyperlink"))
        style = _paragraph_style(block)
        font_size = _maximum_font_size(block)
        markdown_text = _paragraph_markdown(block, relationships) or raw_text

        if font_size >= 44 and raw_text != "Pacote R microdatasus — documentação e código-fonte.":
            output.extend([f"## {raw_text}", ""])
            component_count += 1
        elif style == "Heading2" or (font_size >= 28 and re.match(r"^\d+\.", raw_text)):
            output.extend([f"### {raw_text}", ""])
        elif style == "Heading3" or (font_size >= 26 and re.match(r"^\d+\.\d+\.", raw_text)):
            output.extend([f"#### {raw_text}", ""])
        elif raw_text in EQUATION_TEX:
            equations_seen.add(raw_text)
            output.extend(["$$", EQUATION_TEX[raw_text], "$$", ""])
        elif _is_equation(block, raw_text):
            raise AssertionError(f"Equation lacks an explicit TeX mapping: {raw_text}")
        elif raw_text.startswith("•"):
            output.extend([f"- {markdown_text.lstrip('• ').strip()}", ""])
        else:
            output.extend([markdown_text, ""])
            if raw_text.startswith(COMMENT_NOTE_AFTER):
                output.extend([COMMENT_NOTE, ""])
                note_added = True

    missing_equations = set(EQUATION_TEX) - equations_seen
    if missing_equations:
        raise AssertionError(f"Mapped equations not found in source: {sorted(missing_equations)}")
    diagnostics = {
        "components": component_count,
        "tables": table_count,
        "equations": len(equations_seen),
        "hyperlinks": hyperlink_count,
        "comment_note_added": int(note_added),
    }
    expected = {"components": 7, "tables": 15, "equations": 57, "hyperlinks": 80, "comment_note_added": 1}
    if diagnostics != expected:
        raise AssertionError(f"Unexpected appendix structure: {diagnostics}; expected {expected}")
    markdown = "\n".join(output).rstrip() + "\n"
    remaining_scripts = sorted(set(markdown) & set(SUBSCRIPT_CHARS + SUPERSCRIPT_CHARS + "\u0302"))
    if remaining_scripts:
        raise AssertionError(f"Unicode math scripts remain outside the explicit TeX conversion: {remaining_scripts}")
    OUTPUT.write_text(markdown, encoding="utf-8")
    print(f"PASS: converted appendix to {OUTPUT}")
    print("PASS: " + ", ".join(f"{key}={value}" for key, value in diagnostics.items()))
    return diagnostics


def main() -> int:
    convert()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
