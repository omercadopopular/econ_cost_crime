/* Bilingual interactive presentation layer for retained figure-ready data. */
(() => {
  "use strict";

  const BLUE = "#0879ad", NAVY = "#153b5b", ORANGE = "#d86618", GRAY = "#9aa8b2";
  const PALETTE = ["#56B4E9", "#CC79A7", "#009E73", "#D55E00", "#E69F00", "#0072B2", "#555555", "#8C6BB1"];
  const CONFIG = {
    fig01: ["fig_01_distribuicao_mundial_homicidios.csv", "fig_01_world_homicides_en.csv"],
    fig02a: ["fig_02a_crimes_registrados.csv", "fig_02a_recorded_crime_en.csv"],
    fig02b: ["fig_02b_taxas_criminalidade.csv", "fig_02b_crime_rates_en.csv"],
    fig02c: ["fig_02c_crimes_cobertura_parcial.csv", "fig_02c_partial_coverage_counts_en.csv"],
    fig02d: ["fig_02d_taxas_cobertura_parcial.csv", "fig_02d_partial_coverage_rates_en.csv"],
    fig03: ["fig_03_microrregion_homicides.csv", "fig_03_microregion_homicides_en.csv"],
    fig04: ["fig_04_microrregion_homicide_change.csv", "fig_04_microregion_homicide_change_en.csv"],
    fig05: ["fig_05_microrregion_homicide_convergence.csv", "fig_05_microregion_homicide_convergence_en.csv"],
    fig06: ["fig_06_public_security.csv", "fig_06_public_security_en.csv"],
    fig07: ["fig_07_private_security.csv", "fig_07_private_security_en.csv"],
    fig08: ["fig_08_incarceration.csv", "fig_08_incarceration_en.csv"],
    fig09: ["fig_09_insurance_material_losses.csv", "fig_09_insurance_material_losses_en.csv"],
    fig10: ["fig_10_productive_capacity.csv", "fig_10_productive_capacity_en.csv"],
    fig11: ["fig_11_judicial_costs.csv", "fig_11_judicial_costs_en.csv"],
    fig12: ["fig_12_medical_costs.csv", "fig_12_medical_costs_en.csv"],
    fig13: ["fig_13_total_costs.csv", "fig_13_total_costs_en.csv"],
    fig14: ["fig_14_state_costs.csv", "fig_14_state_costs_en.csv"],
    fig15: ["fig_15_state_trajectories.csv", "fig_15_state_trajectories_en.csv"]
  };

  const I18N = {
    pt: {
      skip: "Pular para o conteúdo", nav_results: "Resultados", nav_figures: "Figuras", nav_method: "Metodologia", nav_downloads: "Downloads",
      eyebrow: "RELATÓRIO 2026", title: "Custos Econômicos da Criminalidade no Brasil", dek: "Uma contabilidade atualizada dos recursos mobilizados e das perdas econômicas associadas ao crime, com séries nacionais de 1996 a 2025 e resultados territoriais.", authors_label: "Autores", download_pdf: "Baixar relatório em PDF", download_word: "Baixar arquivo Word", headline_year: "CUSTO MENSURADO EM 2025", headline_value: "R$ 439,5 bi", headline_share: "3,5% do PIB", headline_note: "Valores em reais de dezembro de 2025",
      findings_eyebrow: "PRINCIPAIS RESULTADOS", findings_title: "A queda da violência letal convive com custos altos e desiguais", finding_1_title: "homicídios por 100 mil", finding_1_text: "Taxa brasileira no UNODC em 2024, abaixo de 30,1 em 2016, mas ainda no percentil 86 da amostra internacional.", finding_2_title: "das microrregiões", finding_2_text: "registraram queda na taxa de homicídios entre 2016 e 2024. A redução foi maior, em média, onde a taxa inicial era mais alta.", finding_3_title: "do custo total", finding_3_text: "correspondia à segurança pública em 2025. Seguros e perdas materiais, custos judiciais e segurança privada também tinham peso expressivo.", finding_4_title: "do PIB estadual", finding_4_text: "era a carga mediana preliminar em 2025; metade das UFs ficou entre 3,2% e 6,4%.", interpretation_title: "Como interpretar o total", interpretation_text: "O agregado combina despesas públicas e privadas, uma transferência previdenciária, prêmios de seguro, perdas materiais e perdas de capacidade produtiva estimadas por modelo. É uma medida contábil ampla da carga econômica associada ao crime — não uma estimativa causal de bem-estar nem do PIB que existiria na ausência de criminalidade.",
      figures_eyebrow: "EXPLORE OS DADOS", figures_title: "Quinze figuras interativas", figures_intro: "Passe o cursor para consultar valores, use os controles das figuras e baixe o CSV exato que sustenta cada visualização.", filter_all: "Todas", filter_crime: "Crime e homicídios", filter_national: "Custos nacionais", filter_states: "Estados", csv: "Baixar CSV",
      chart_01: "Brasil na distribuição internacional de homicídios", chart_02a: "Crimes registrados — contagens", chart_02b: "Crimes registrados — taxas", chart_02c: "Crimes patrimoniais — cobertura parcial", chart_02d: "Taxas de crimes patrimoniais — cobertura parcial", chart_03: "Distribuição dos homicídios nas microrregiões", chart_04: "Mudança geográfica dos homicídios", chart_05: "Convergência das taxas de homicídio", chart_06: "Segurança pública", chart_07: "Segurança privada", chart_08: "Encarceramento e auxílio-reclusão", chart_09: "Seguros e perdas materiais", chart_10: "Perda de capacidade produtiva", chart_11: "Custos judiciais", chart_12: "Serviços médico-terapêuticos", chart_13: "Custos econômicos mensurados da criminalidade", chart_14: "Nível e composição dos custos estaduais", chart_15: "Trajetória da renda e do custo por UF",
      note_01: "Comparação entre 87 países ou territórios observados em 2016 e 2024; percentis sem ponderação populacional.", note_13: "Use o seletor para alternar entre valores reais, percentual do PIB e composição do total.", state_warning: "Resultados estaduais de 2025 são preliminares e serão atualizados antes da publicação final.",
      method_eyebrow: "COMO MEDIMOS", method_title: "Uma contabilidade ampla, com conceitos preservados", method_intro: "As séries reúnem sete canais econômicos. Cada um tem fonte, convenção monetária e interpretação próprias; a agregação não transforma objetos diferentes em perdas de bem-estar equivalentes.", method_public: "Segurança pública", method_public_text: "Despesas da União, estados, Distrito Federal e municípios classificadas na função Segurança Pública.", method_private: "Segurança privada", method_private_text: "Custo do trabalho formal e massa de rendimentos do trabalho informal em ocupações de vigilância e proteção.", method_prison: "Encarceramento", method_prison_text: "Custódia e reintegração social, além do auxílio-reclusão, explicitamente tratado como transferência.", method_material: "Seguros e perdas", method_material_text: "Prêmios de seguro e perdas materiais estimadas para veículos, patrimônio e transporte de cargas.", method_productive: "Capacidade produtiva", method_productive_text: "Valor presente da renda esperada não produzida por vítimas de homicídio — uma perda modelada, não uma despesa observada.", method_justice: "Custos judiciais", method_justice_text: "Parcela criminal dos tribunais e Ministérios Públicos, acrescida dos serviços de defesa valorados.", method_health: "Serviços médicos", method_health_text: "Internações no SUS associadas a agressões e perda produtiva temporária durante a hospitalização.",
      downloads_eyebrow: "RELATÓRIO E DADOS", downloads_title: "Continue a análise", full_report: "Relatório completo", pdf_desc: "Versão diagramada com apêndice metodológico.", word_report: "Versão editável", word_desc: "Arquivo Word para revisão substantiva.", source_report: "Texto-fonte", md_desc: "Manuscrito em Markdown, com referências às figuras.", repository: "Repositório", repo_desc: "Código, dados processados e documentação metodológica.", footer: "Publicação do Inter-American Dialogue — Brazil Program. Cálculos dos autores com dados das fontes identificadas em cada figura.",
      real: "Valores reais", gdp: "% do PIB", composition: "% do total", year: "Ano", billions: "R$ bilhões de dez./2025", shareGDP: "Percentual do PIB", shareTotal: "Percentual do total", population: "População", rate: "Homicídios por 100 mil habitantes", percentile: "Percentil", change: "Variação por 100 mil habitantes", initialRate: "Taxa em 2016", gdpPc: "PIB per capita real (R$ mil)", stateBurden: "Custos (% do PIB estadual)", states: "UFs", countThousands: "Milhares", victimRate: "Vítimas por 100 mil", incidentRate: "Ocorrências por 100 mil", error: "Não foi possível carregar esta visualização. Atualize a página ou use o download do CSV."
    },
    en: {
      skip: "Skip to content", nav_results: "Findings", nav_figures: "Figures", nav_method: "Methodology", nav_downloads: "Downloads",
      eyebrow: "2026 REPORT", title: "The Economic Costs of Crime in Brazil", dek: "An updated accounting of the resources mobilized and economic losses associated with crime, with national series from 1996 to 2025 and territorial results.", authors_label: "Authors", download_pdf: "Download the PDF report", download_word: "Download the Word file", headline_year: "MEASURED COST IN 2025", headline_value: "R$439.5bn", headline_share: "3.5% of GDP", headline_note: "Values in December 2025 reais",
      findings_eyebrow: "KEY FINDINGS", findings_title: "The decline in lethal violence coexists with high and unequal costs", finding_1_title: "homicides per 100,000", finding_1_text: "Brazil’s UNODC rate in 2024, down from 30.1 in 2016 but still at the 86th percentile of the international sample.", finding_2_title: "of microregions", finding_2_text: "recorded a decline in homicide rates between 2016 and 2024. On average, the reduction was larger where the initial rate was higher.", finding_3_title: "of the total cost", finding_3_text: "was public-security expenditure in 2025. Insurance and material losses, judicial costs, and private security also had substantial shares.", finding_4_title: "of state GDP", finding_4_text: "was the preliminary median burden in 2025; half of the states lay between 3.2% and 6.4%.", interpretation_title: "How to interpret the total", interpretation_text: "The aggregate combines public and private expenditure, a social-security transfer, insurance premiums, material losses, and modeled productive-capacity losses. It is a broad accounting measure of the economic burden associated with crime—not a causal welfare estimate or the GDP that would exist without crime.",
      figures_eyebrow: "EXPLORE THE DATA", figures_title: "Fifteen interactive figures", figures_intro: "Hover to inspect values, use the figure controls, and download the exact CSV underlying each visualization.", filter_all: "All", filter_crime: "Crime and homicide", filter_national: "National costs", filter_states: "States", csv: "Download CSV",
      chart_01: "Brazil in the international homicide distribution", chart_02a: "Recorded crime — counts", chart_02b: "Recorded crime — rates", chart_02c: "Property crime — partial coverage", chart_02d: "Property-crime rates — partial coverage", chart_03: "Distribution of homicide across microregions", chart_04: "Geographic change in homicide", chart_05: "Convergence in homicide rates", chart_06: "Public security", chart_07: "Private security", chart_08: "Incarceration and the incarceration benefit", chart_09: "Insurance and material losses", chart_10: "Productive-capacity losses", chart_11: "Judicial costs", chart_12: "Medical and therapeutic services", chart_13: "Measured economic costs of crime", chart_14: "Level and composition of state costs", chart_15: "State trajectories in income and crime costs",
      note_01: "Comparison across 87 countries or territories observed in 2016 and 2024; percentiles are not population-weighted.", note_13: "Use the selector to switch among real values, share of GDP, and share of the total.", state_warning: "The 2025 state results are preliminary and will be updated before final publication.",
      method_eyebrow: "HOW WE MEASURE", method_title: "A broad accounting framework that preserves conceptual distinctions", method_intro: "The series cover seven economic channels. Each has its own source, monetary convention, and interpretation; aggregation does not turn different objects into equivalent welfare losses.", method_public: "Public security", method_public_text: "Federal, state, Federal District, and municipal spending classified under the Public Security function.", method_private: "Private security", method_private_text: "Formal labor costs and informal labor income in surveillance and protection occupations.", method_prison: "Incarceration", method_prison_text: "Custody and social reintegration plus the incarceration benefit, explicitly treated as a transfer.", method_material: "Insurance and losses", method_material_text: "Insurance premiums and estimated material losses for vehicles, property, and cargo transport.", method_productive: "Productive capacity", method_productive_text: "Present value of expected income not produced by homicide victims—a modeled loss, not observed expenditure.", method_justice: "Judicial costs", method_justice_text: "Crime-related shares of courts and prosecutors plus valued criminal-defense services.", method_health: "Medical services", method_health_text: "SUS hospital admissions associated with assault and temporary productive loss during hospitalization.",
      downloads_eyebrow: "REPORT AND DATA", downloads_title: "Continue the analysis", full_report: "Full report", pdf_desc: "Designed English edition of the report.", word_report: "Editable version", word_desc: "Word file for substantive review.", source_report: "Source text", md_desc: "Markdown manuscript with figure references.", repository: "Repository", repo_desc: "Code, processed data, and methodological documentation.", footer: "Published by the Inter-American Dialogue — Brazil Program. Authors’ calculations using the sources identified in each figure.",
      real: "Real values", gdp: "% of GDP", composition: "% of total", year: "Year", billions: "R$ billions, Dec. 2025", shareGDP: "Share of GDP", shareTotal: "Share of total", population: "Population", rate: "Homicides per 100,000 inhabitants", percentile: "Percentile", change: "Change per 100,000 inhabitants", initialRate: "2016 rate", gdpPc: "Real GDP per capita (R$ thousands)", stateBurden: "Costs (% of state GDP)", states: "States", countThousands: "Thousands", victimRate: "Victims per 100,000", incidentRate: "Incidents per 100,000", error: "This visualization could not be loaded. Refresh the page or use the CSV download."
    }
  };

  const requestedLanguage = new URLSearchParams(window.location.search).get("lang");
  let language = requestedLanguage === "en" || requestedLanguage === "pt"
    ? requestedLanguage
    : (localStorage.getItem("cec-language") === "en" ? "en" : "pt");
  const cache = new Map();
  let geojson;

  function parseCSV(text) {
    const rows = []; let row = [], field = "", quoted = false;
    for (let i = 0; i < text.length; i += 1) {
      const char = text[i];
      if (char === '"') {
        if (quoted && text[i + 1] === '"') { field += '"'; i += 1; } else quoted = !quoted;
      } else if (char === ',' && !quoted) { row.push(field); field = ""; }
      else if ((char === '\n' || char === '\r') && !quoted) {
        if (char === '\r' && text[i + 1] === '\n') i += 1;
        row.push(field); if (row.some(value => value !== "")) rows.push(row); row = []; field = "";
      } else field += char;
    }
    if (field || row.length) { row.push(field); rows.push(row); }
    const headers = rows.shift() || [];
    return rows.map(values => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
  }

  const num = value => Number(value);
  const unique = values => [...new Set(values)];
  const t = key => I18N[language][key] || key;
  const fmt = (value, digits = 1) => new Intl.NumberFormat(language === "pt" ? "pt-BR" : "en-US", {maximumFractionDigits: digits, minimumFractionDigits: digits}).format(value);

  async function dataFor(id) {
    const key = `${language}:${id}`;
    if (cache.has(key)) return cache.get(key);
    const file = CONFIG[id][language === "pt" ? 0 : 1];
    const response = await fetch(`data/${language}/${file}`);
    if (!response.ok) throw new Error(`${response.status} ${file}`);
    const rows = parseCSV(await response.text()); cache.set(key, rows); return rows;
  }

  const commonLayout = () => ({
    paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: {family: "Arial, sans-serif", color: "#253743", size: 12},
    margin: {l: 62, r: 22, t: 42, b: 62}, hoverlabel: {bgcolor: "#fff", bordercolor: "#153b5b"},
    xaxis: {showgrid: false, zeroline: false, linecolor: "#8fa0aa", tickfont: {size: 11}},
    yaxis: {gridcolor: "#d9e1e6", zerolinecolor: "#6b7b85", tickfont: {size: 11}},
    legend: {orientation: "h", y: 1.08, x: 0, font: {size: 11}}
  });
  const plotConfig = {responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d"]};
  function render(id, traces, layout) { return Plotly.react(`chart-${id}`, traces, {...commonLayout(), ...layout}, plotConfig); }

  async function fig01() {
    const rows = await dataFor("fig01"), years = unique(rows.map(r => num(r.year))).sort();
    const traces = [];
    years.forEach((year, index) => {
      const subset = rows.filter(r => num(r.year) === year && num(r.is_brazil) === 0);
      traces.push({type: "scatter", mode: "markers", x: subset.map(r => num(r.percentile_unweighted)), y: subset.map(r => num(r.homicide_rate_per_100k)), text: subset.map(r => r.country), name: String(year), marker: {color: index ? "#8ba3b1" : "#b7c1c7", size: 7, opacity: .58}, hovertemplate: "%{text}<br>%{y:.1f}<br>p%{x:.1f}<extra></extra>", xaxis: index ? "x2" : "x", yaxis: index ? "y2" : "y"});
      const br = rows.find(r => num(r.year) === year && num(r.is_brazil) === 1);
      traces.push({type: "scatter", mode: "markers+text", x: [num(br.percentile_unweighted)], y: [num(br.homicide_rate_per_100k)], text: ["Brazil"], textposition: "top left", name: `Brazil ${year}`, marker: {color: ORANGE, size: 15, symbol: "diamond"}, hovertemplate: `Brazil ${year}<br>%{y:.1f}<br>p%{x:.1f}<extra></extra>`, xaxis: index ? "x2" : "x", yaxis: index ? "y2" : "y", showlegend: false});
    });
    const maxY = Math.ceil(Math.max(...rows.map(r => num(r.homicide_rate_per_100k))) / 10) * 10;
    return render("fig01", traces, {grid: {rows: 1, columns: 2, pattern: "independent", xgap: .12}, xaxis: {title: t("percentile"), range: [0, 101]}, xaxis2: {title: t("percentile"), range: [0, 101]}, yaxis: {title: t("rate"), range: [0, maxY]}, yaxis2: {range: [0, maxY]}, annotations: years.map((year, i) => ({text: `<b>${year}</b>`, xref: "paper", yref: "paper", x: i ? .56 : 0, y: 1.08, showarrow: false, xanchor: "left"}))});
  }

  async function figure2(id) {
    const rows = await dataFor(id), crimes = unique(rows.map(r => r.crime));
    const cols = 2, nRows = Math.ceil(crimes.length / cols), gapX = .1, gapY = .12;
    const rate = id.endsWith("b") || id.endsWith("d");
    const traces = [], layout = {showlegend: false, margin: {l: 58, r: 20, t: 40, b: 48}, annotations: []};
    crimes.forEach((crime, index) => {
      const subset = rows.filter(r => r.crime === crime).sort((a,b) => num(a.year) - num(b.year));
      const suffix = index === 0 ? "" : String(index + 1);
      const values = subset.map(r => rate ? num(r.plotted_value) : num(r.plotted_value) / 1000);
      traces.push({type: "bar", x: subset.map(r => num(r.year)), y: values, marker: {color: PALETTE[index % PALETTE.length]}, xaxis: `x${suffix}`, yaxis: `y${suffix}`, name: crime, hovertemplate: `%{x}<br>${crime}: %{y:${rate ? ".1f" : ",.1f"}}<extra></extra>`});
      const col = index % cols, row = Math.floor(index / cols), width = (1-gapX)/cols, height = (1-gapY*(nRows-1))/nRows;
      const x0 = col * (width+gapX), y1 = 1 - row*(height+gapY), y0 = y1-height;
      layout[`xaxis${suffix}`] = {domain: [x0, x0+width], anchor: `y${suffix}`, showgrid: false, tickmode: "linear", dtick: 1, tickangle: -45};
      layout[`yaxis${suffix}`] = {domain: [y0,y1], anchor: `x${suffix}`, gridcolor: "#d9e1e6", rangemode: "tozero"};
      layout.annotations.push({text: `<b>${crime}</b>`, xref: "paper", yref: "paper", x: x0, y: Math.min(1.08,y1+.035), xanchor: "left", showarrow: false, font: {size: 13, color: NAVY}});
    });
    layout.annotations.push({text: rate ? (id.endsWith("b") ? t("victimRate") : t("incidentRate")) : t("countThousands"), xref: "paper", yref: "paper", x: -.055, y: .5, textangle: -90, showarrow: false});
    return render(id, traces, layout);
  }

  async function fig03() {
    const rows = await dataFor("fig03"), populations = rows.map(r => num(r.population)), maxPop = Math.max(...populations);
    return render("fig03", [{type: "scatter", mode: "markers", x: rows.map(r => num(r.percentile_unweighted)), y: rows.map(r => num(r.homicide_rate_per_100k)), text: rows.map(r => `${r.microrregion_name} (${r.uf})`), customdata: populations, marker: {color: BLUE, opacity: .48, size: populations.map(v => 7 + 42*Math.sqrt(v/maxPop)), line: {color: NAVY, width: .5}}, hovertemplate: "%{text}<br>Taxa: %{y:.1f}<br>Percentil: %{x:.1f}<br>Pop.: %{customdata:,.0f}<extra></extra>"}], {xaxis: {title: t("percentile"), range: [0,101]}, yaxis: {title: t("rate"), rangemode: "tozero"}, showlegend: false});
  }

  async function fig04() {
    const rows = await dataFor("fig04");
    if (!geojson) geojson = await (await fetch("data/geography/ibge_2015_microregions_simplified.geojson")).json();
    const limit = num(rows[0].visual_scale_limit);
    return render("fig04", [{type: "choropleth", geojson, locations: rows.map(r => r.microrregion_code), z: rows.map(r => num(r.visual_value_clipped)), customdata: rows.map(r => [r.microrregion_name, r.uf, num(r.delta_rate_per_100k)]), featureidkey: "properties.code", colorscale: [[0,"#2166ac"],[.5,"#f7f7f7"],[1,"#b2182b"]], zmin: -limit, zmax: limit, marker: {line: {color: "rgba(255,255,255,.35)", width: .25}}, colorbar: {title: t("change"), thickness: 12}, hovertemplate: "%{customdata[0]} (%{customdata[1]})<br>%{customdata[2]:+.1f}<extra></extra>"}], {geo: {fitbounds: "locations", visible: false, projection: {type: "mercator"}}, margin: {l: 8,r: 8,t: 8,b: 8}});
  }

  async function fig05() {
    const rows = await dataFor("fig05"), maxPop = Math.max(...rows.map(r => num(r.population_2016)));
    const sorted = [...rows].sort((a,b) => num(a.rate_2016_per_100k)-num(b.rate_2016_per_100k));
    const traces = [{type:"scatter",mode:"markers",x:rows.map(r=>num(r.rate_2016_per_100k)),y:rows.map(r=>num(r.delta_rate_2016_2024_per_100k)),text:rows.map(r=>`${r.microrregion_name} (${r.uf})`),customdata:rows.map(r=>num(r.population_2016)),marker:{color:BLUE,opacity:.43,size:rows.map(r=>6+36*Math.sqrt(num(r.population_2016)/maxPop)),line:{color:NAVY,width:.4}},hovertemplate:"%{text}<br>2016: %{x:.1f}<br>Δ: %{y:+.1f}<br>Pop.: %{customdata:,.0f}<extra></extra>"},{type:"scatter",mode:"lines",x:sorted.map(r=>num(r.rate_2016_per_100k)),y:sorted.map(r=>num(r.population_weighted_fitted_delta)),name: language === "pt" ? "Ajuste ponderado" : "Weighted fit",line:{color:ORANGE,width:3,dash:"dash"},hoverinfo:"skip"}];
    return render("fig05",traces,{xaxis:{title:t("initialRate"),rangemode:"tozero"},yaxis:{title:t("change"),zeroline:true,zerolinecolor:"#4a5a64"},legend:{orientation:"h",y:1.08}});
  }

  const componentColors = label => {
    const names = {
      "Serviços médico-terapêuticos":"#56B4E9","Medical and therapeutic services":"#56B4E9","Encarceramento e auxílio-reclusão":"#CC79A7","Incarceration and incarceration benefit":"#CC79A7","Custos judiciais":"#009E73","Judicial costs":"#009E73","Perda de capacidade produtiva":"#D55E00","Productive-capacity losses":"#D55E00","Seguros e perdas materiais":"#E69F00","Insurance and material losses":"#E69F00","Segurança privada":"#0072B2","Private security":"#0072B2","Segurança pública":"#555555","Public security":"#555555","Total":"#111111"
    }; return names[label];
  };

  async function componentFigure(id) {
    const rows = await dataFor(id), allComponents = unique(rows.map(r=>r.componente)).filter(c=>c!=="Total"), components = allComponents.length ? allComponents : unique(rows.map(r=>r.componente));
    const metrics = [{field:"valor_reais_dez_2025",scale:1e9,label:t("real"),axis:t("billions")},{field:"participacao_pib_pct",scale:1,label:t("gdp"),axis:t("shareGDP")},{field:"composicao_pct",scale:1,label:t("composition"),axis:t("shareTotal")}];
    const traces=[];
    metrics.forEach((metric,metricIndex)=>components.forEach((component,index)=>{
      let subset=rows.filter(r=>r.componente===component && (!r.serie || r.serie!=="total")).sort((a,b)=>num(a.ano)-num(b.ano));
      if(!subset.length) subset=rows.filter(r=>r.componente===component).sort((a,b)=>num(a.ano)-num(b.ano));
      traces.push({type:"bar",x:subset.map(r=>num(r.ano)),y:subset.map(r=>num(r[metric.field])/metric.scale),name:component,legendgroup:component,marker:{color:componentColors(component)||PALETTE[index%PALETTE.length]},visible:metricIndex===0,hovertemplate:`%{x}<br>${component}: %{y:.2f}<extra></extra>`});
    }));
    if(id==="fig06") {
      metrics.slice(0,2).forEach((metric,metricIndex)=>{
        const total=rows.filter(r=>r.serie==="total").sort((a,b)=>num(a.ano)-num(b.ano));
        traces.push({type:"scatter",mode:"lines+markers",x:total.map(r=>num(r.ano)),y:total.map(r=>num(r[metric.field])/metric.scale),name:"Total",legendgroup:"Total",line:{color:"#111",width:2},marker:{size:4},visible:metricIndex===0,hovertemplate:"%{x}<br>Total: %{y:.2f}<extra></extra>"});
      });
    }
    const tracesPerMetric=components.length, totalTraces=traces.length;
    const buttons=metrics.map((metric,index)=>({label:metric.label,method:"update",args:[{visible:Array.from({length:totalTraces},(_,traceIndex)=>{
      if(traceIndex<3*tracesPerMetric) return Math.floor(traceIndex/tracesPerMetric)===index;
      return id==="fig06" && index<2 && traceIndex===3*tracesPerMetric+index;
    })},{"yaxis.title":metric.axis,"yaxis.ticksuffix":index?"%":""}]}));
    return render(id,traces,{barmode:"stack",xaxis:{title:t("year"),dtick: id==="fig06"||id==="fig13" ? 2:1},yaxis:{title:t("billions"),rangemode:"tozero"},legend:{orientation:"h",y:1.18},updatemenus:[{type:"buttons",direction:"right",x:0,y:1.1,buttons,bgcolor:"#eef3f6",bordercolor:"#c4d1d9",font:{size:11}}],margin:{l:65,r:20,t:88,b:55}});
  }

  async function fig14() {
    const rows=await dataFor("fig14"), stateRows=[];
    unique(rows.map(r=>r.uf)).forEach(uf=>stateRows.push(rows.find(r=>r.uf===uf)));
    const ordered=[...stateRows].sort((a,b)=>num(a.custo_total_pib_pct)-num(b.custo_total_pib_pct));
    const components=unique(rows.map(r=>r.componente));
    const traces=[{type:"scatter",mode:"markers+text",x:stateRows.map(r=>num(r.pib_per_capita_reais_dez_2025)/1000),y:stateRows.map(r=>num(r.custo_total_pib_pct)),text:stateRows.map(r=>r.uf),textposition:"top center",marker:{color:BLUE,size:8},hovertemplate:"%{text}<br>PIB pc: R$ %{x:,.1f} mil<br>Custo: %{y:.1f}%<extra></extra>",xaxis:"x",yaxis:"y",showlegend:false}];
    components.forEach((component,index)=>{const lookup=new Map(rows.filter(r=>r.componente===component).map(r=>[r.uf,r]));traces.push({type:"bar",orientation:"h",y:ordered.map(r=>r.uf),x:ordered.map(r=>num(lookup.get(r.uf).participacao_pib_pct)),name:component,marker:{color:componentColors(component)||PALETTE[index%PALETTE.length]},xaxis:"x2",yaxis:"y2",hovertemplate:`%{y}<br>${component}: %{x:.2f}%<extra></extra>`});});
    return render("fig14",traces,{barmode:"stack",xaxis:{domain:[0,.45],title:t("gdpPc")},yaxis:{domain:[0,1],title:t("stateBurden")},xaxis2:{domain:[.56,1],title:t("shareGDP"),ticksuffix:"%"},yaxis2:{domain:[0,1],anchor:"x2",categoryorder:"array",categoryarray:ordered.map(r=>r.uf),tickfont:{size:9}},legend:{orientation:"h",y:1.14,x:.5,xanchor:"center"},margin:{l:58,r:24,t:92,b:62}});
  }

  async function fig15() {
    const rows=await dataFor("fig15"), ufs=unique(rows.map(r=>r.uf)), starts=[],ends=[],annotations=[];
    ufs.forEach(uf=>{const pair=rows.filter(r=>r.uf===uf).sort((a,b)=>num(a.ano)-num(b.ano));const s=pair[0],e=pair[pair.length-1];starts.push(s);ends.push(e);annotations.push({xref:"x",yref:"y",ax:num(s.pib_per_capita_reais_dez_2025)/1000,ay:num(s.custo_total_pib_pct),x:num(e.pib_per_capita_reais_dez_2025)/1000,y:num(e.custo_total_pib_pct),showarrow:true,arrowhead:2,arrowsize:1,arrowwidth:1.1,arrowcolor:"#7893a5",opacity:.75,text:""});});
    const traces=[{type:"scatter",mode:"markers",x:starts.map(r=>num(r.pib_per_capita_reais_dez_2025)/1000),y:starts.map(r=>num(r.custo_total_pib_pct)),text:starts.map(r=>r.uf),name:"2016",marker:{symbol:"square-open",color:"#4b5961",size:9},hovertemplate:"%{text} 2016<br>PIB pc: R$ %{x:,.1f} mil<br>Custo: %{y:.1f}%<extra></extra>"},{type:"scatter",mode:"markers+text",x:ends.map(r=>num(r.pib_per_capita_reais_dez_2025)/1000),y:ends.map(r=>num(r.custo_total_pib_pct)),text:ends.map(r=>r.uf),textposition:"middle right",name:"2025",marker:{color:ORANGE,size:8},hovertemplate:"%{text} 2025<br>PIB pc: R$ %{x:,.1f} mil<br>Custo: %{y:.1f}%<extra></extra>"}];
    return render("fig15",traces,{xaxis:{title:t("gdpPc"),rangemode:"tozero"},yaxis:{title:t("stateBurden"),ticksuffix:"%",rangemode:"tozero"},annotations,legend:{orientation:"h",y:1.08}});
  }

  const renderers={fig01,fig02a:()=>figure2("fig02a"),fig02b:()=>figure2("fig02b"),fig02c:()=>figure2("fig02c"),fig02d:()=>figure2("fig02d"),fig03,fig04,fig05,fig06:()=>componentFigure("fig06"),fig07:()=>componentFigure("fig07"),fig08:()=>componentFigure("fig08"),fig09:()=>componentFigure("fig09"),fig10:()=>componentFigure("fig10"),fig11:()=>componentFigure("fig11"),fig12:()=>componentFigure("fig12"),fig13:()=>componentFigure("fig13"),fig14,fig15};

  function updateDownloads() {
    document.querySelectorAll(".csv-download").forEach(link=>{const id=link.dataset.csv, file=CONFIG[id][language==="pt"?0:1];link.href=`data/${language}/${file}`;link.download=file;});
    const suffix=language==="pt"?"":"-en";
    document.querySelectorAll(".report-pdf").forEach(link=>link.href=`downloads/report${suffix}.pdf`);
    document.querySelectorAll(".report-word").forEach(link=>link.href=`downloads/report${suffix}.docx`);
    document.querySelectorAll(".report-md").forEach(link=>link.href=`downloads/report${suffix}.md`);
  }

  async function renderAll() {
    for (const [id, renderer] of Object.entries(renderers)) {
      try { await renderer(); }
      catch (error) {
        console.error(id,error);
        const node = document.getElementById(`chart-${id}`);
        node.dataset.renderError = error instanceof Error ? error.message : String(error);
        node.innerHTML=`<div class="chart-error">${t("error")}</div>`;
      }
    }
  }

  async function setLanguage(next) {
    language=next;localStorage.setItem("cec-language",language);document.documentElement.lang=language==="pt"?"pt-BR":"en";
    const url = new URL(window.location.href); url.searchParams.set("lang", language); history.replaceState({}, "", url);
    document.title=I18N[language].title;
    document.querySelectorAll("[data-i18n]").forEach(node=>{const value=I18N[language][node.dataset.i18n];if(value)node.textContent=value;});
    document.querySelectorAll("[data-language]").forEach(button=>{const active=button.dataset.language===language;button.classList.toggle("active",active);button.setAttribute("aria-pressed",String(active));});
    updateDownloads();await renderAll();
  }

  function setupFilters() { document.querySelectorAll("[data-filter]").forEach(button=>button.addEventListener("click",()=>{document.querySelectorAll("[data-filter]").forEach(item=>item.classList.remove("active"));button.classList.add("active");const filter=button.dataset.filter;document.querySelectorAll(".chart-card").forEach(card=>card.classList.toggle("hidden",filter!=="all"&&card.dataset.topic!==filter));setTimeout(()=>window.dispatchEvent(new Event("resize")),30);})); }

  window.addEventListener("DOMContentLoaded",async()=>{
    setupFilters(); document.querySelectorAll("[data-language]").forEach(button=>button.addEventListener("click",()=>setLanguage(button.dataset.language)));
    if(typeof Plotly==="undefined"){document.querySelectorAll(".chart").forEach(node=>node.innerHTML=`<div class="chart-error">${t("error")}</div>`);return;}
    await setLanguage(language);
    if (window.location.hash) {
      document.querySelector(window.location.hash)?.scrollIntoView({block: "start"});
    }
  });
})();
