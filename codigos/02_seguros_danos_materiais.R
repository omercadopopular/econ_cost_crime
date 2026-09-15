# ==============================================================================
# 02 — SEGUROS E DANOS MATERIAIS
# Projeto: Custos da Criminalidade no Brasil, 1996-2025
# ==============================================================================
# Escopo deste arquivo
# Contém somente as rotinas finais em R aplicadas às bases SES/Susep: prêmios e perdas patrimoniais/de carga. A série histórica, o preço AutoSeg, quantidades de veículos, recuperação e consolidação anual permanecem na planilha final. O antigo script FIPE/IVR foi excluído por não integrar o método final.
#
# Reprodutibilidade
# 1. Ajuste somente os caminhos em "CONFIGURACAO".
# 2. Instale previamente os pacotes listados; o script não instala pacotes.
# 3. As etapas feitas em Excel são identificadas e não são recriadas aqui.
# 4. As saídas são gravadas em dir_saida sem chamadas interativas.
# ==============================================================================


options(stringsAsFactors = FALSE, survey.lonely.psu = "adjust")


# CONFIGURACAO ---------------------------------------------------------------
dir_susep <- "dados/susep"
arquivo_serie_final <- "dados/serie_final_gastos_seguros_e_perdas_1996_a_2025_atualizada.xlsm"
dir_saida <- "resultados/seguros_danos_materiais"
dir.create(dir_saida, recursive = TRUE, showWarnings = FALSE)


pacotes <- c("tidyverse","data.table","readxl","writexl")
faltantes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]
if (length(faltantes)) stop("Instale os pacotes: ", paste(faltantes, collapse = ", "))




# ============================================================
# GASTOS COM SEGUROS — SUSEP/SES, 2010–2025
# CLASSIFICAÇÃO DOCUMENTAL REVISADA
# ============================================================
# Medida principal: prêmio direto.
# A classificação é lida diretamente da planilha-mestra revisada.
# O script também recalcula a classificação original para produzir
# uma comparação anual perfeitamente consistente na mesma extração.


# ============================================================
# 1. CAMINHOS
# ============================================================


pasta_base <- dir_susep
pasta_downloads <- dir_saida


arquivo_ramos <- file.path(pasta_base, "Ses_ramos.csv")
arquivo_seguros <- file.path(pasta_base, "Ses_seguros.csv")
arquivo_classificacao <- arquivo_serie_final
arquivo_saida <- file.path(
  pasta_downloads,
  "resultados_gastos_com_seguros_2010_2025_classificacao_revisada.xlsx"
)


arquivos_necessarios <- c(
  arquivo_ramos,
  arquivo_seguros,
  arquivo_classificacao
)


if (any(!file.exists(arquivos_necessarios))) {
  stop(
    paste0(
      "Arquivo(s) não encontrado(s):\n",
      paste(arquivos_necessarios[!file.exists(arquivos_necessarios)], collapse = "\n")
    )
  )
}


# ============================================================
# 2. FUNÇÕES AUXILIARES
# ============================================================


converter_numero <- function(x) {
  if (is.numeric(x)) return(as.numeric(x))
  
  x <- trimws(as.character(x))
  x[x %in% c("", "NA", "N/A", "...", "-")] <- NA_character_
  possui_virgula <- grepl(",", x, fixed = TRUE)
  resultado <- rep(NA_real_, length(x))
  
  resultado[possui_virgula] <- as.numeric(
    gsub(
      ",", ".",
      gsub(".", "", x[possui_virgula], fixed = TRUE),
      fixed = TRUE
    )
  )
  resultado[!possui_virgula] <- as.numeric(x[!possui_virgula])
  resultado
}


soma_segura <- function(x) {
  if (all(is.na(x))) NA_real_ else sum(x, na.rm = TRUE)
}


normalizar_decisao <- function(x) {
  str_to_lower(str_trim(as.character(x))) == "incluir"
}


# ============================================================
# 3. IMPORTAR E VALIDAR A CLASSIFICAÇÃO REVISADA
# ============================================================


classificacao_bruta <- read_excel(
  arquivo_classificacao,
  sheet = "Tabela de Correspondência - SUS",
  skip = 0,
  col_types = "text"
)


colunas_classificacao <- c(
  "Código", "Ramo oficial", "Cenário amplo", "Cenário conservador"
)


if (!all(colunas_classificacao %in% names(classificacao_bruta))) {
  stop("A planilha de classificação não contém as colunas esperadas.")
}


classificacao_revisada <- classificacao_bruta %>%
  transmute(
    coramo = as.integer(`Código`),
    ramo_documentado = as.character(`Ramo oficial`),
    cenario_amplo_revisado = normalizar_decisao(`Cenário amplo`),
    cenario_conservador_revisado = normalizar_decisao(`Cenário conservador`)
  ) %>%
  filter(!is.na(coramo))


if (nrow(classificacao_revisada) != 161) {
  stop(
    paste(
      "Esperavam-se 161 códigos na classificação; foram encontrados",
      nrow(classificacao_revisada)
    )
  )
}


if (anyDuplicated(classificacao_revisada$coramo)) {
  stop("Há códigos duplicados na classificação revisada.")
}


if (any(
  classificacao_revisada$cenario_conservador_revisado &
  !classificacao_revisada$cenario_amplo_revisado
)) {
  stop("Há ramo conservador que não pertence ao cenário amplo.")
}


# Grupos analíticos do projeto. O ramo cibernético fica separado
# para não ser ocultado dentro do grupo patrimonial.
codigos_automotivos_revisados <- c(526, 531)
codigos_ciberneticos_revisados <- c(327)
codigos_transporte_revisados <- c(
  621, 622, 627, 632, 638, 652, 654, 655, 656, 658
)


classificacao_revisada <- classificacao_revisada %>%
  mutate(
    categoria_projeto_revisada = case_when(
      coramo %in% codigos_automotivos_revisados ~ "automotivo",
      coramo %in% codigos_ciberneticos_revisados ~ "riscos_ciberneticos",
      coramo %in% codigos_transporte_revisados ~ "transporte_carga",
      cenario_amplo_revisado ~ "patrimonial",
      TRUE ~ "fora_escopo"
    )
  )


contagem_classificacao <- classificacao_revisada %>%
  summarise(
    ramos_total = n(),
    amplo = sum(cenario_amplo_revisado),
    conservador = sum(cenario_conservador_revisado)
  )


if (
  contagem_classificacao$amplo != 26 ||
  contagem_classificacao$conservador != 10
) {
  stop("A classificação não reproduz 26 ramos amplos e 10 conservadores.")
}


# ============================================================
# 4. IMPORTAR AS BASES DA SUSEP
# ============================================================


ses_ramos <- fread(
  arquivo_ramos,
  sep = ";",
  encoding = "Latin-1"
)


ses_seguros <- fread(
  arquivo_seguros,
  sep = ";",
  encoding = "Latin-1"
)


colunas_monetarias_desejadas <- c(
  "premio_direto", "premio_de_seguros", "premio_retido",
  "premio_ganho", "sinistro_direto", "sinistro_retido", "desp_com"
)
colunas_monetarias <- intersect(
  colunas_monetarias_desejadas,
  names(ses_seguros)
)


if (!all(c("coramo", "noramo") %in% names(ses_ramos))) {
  stop("Ses_ramos.csv não contém coramo e noramo.")
}
if (!all(c("damesano", "coramo", "premio_direto", "premio_ganho") %in%
         names(ses_seguros))) {
  stop("Ses_seguros.csv não contém as colunas essenciais.")
}


ses_seguros[
  ,
  (colunas_monetarias) := lapply(.SD, converter_numero),
  .SDcols = colunas_monetarias
]


ses_seguros <- ses_seguros %>%
  mutate(
    ano = floor(damesano / 100),
    mes = damesano %% 100
  )


# ============================================================
# 5. RECONCILIAR CADASTRO, CLASSIFICAÇÃO E BASE OPERACIONAL
# ============================================================


duplicacoes_ramos <- ses_ramos %>%
  count(coramo, sort = TRUE) %>%
  filter(n > 1)
if (nrow(duplicacoes_ramos) > 0) stop("Ses_ramos.csv possui coramo duplicado.")


codigos_classificacao_ausentes_cadastro <- classificacao_revisada %>%
  anti_join(ses_ramos %>% select(coramo), by = "coramo")


codigos_cadastro_ausentes_classificacao <- ses_ramos %>%
  anti_join(classificacao_revisada %>% select(coramo), by = "coramo")


if (nrow(codigos_classificacao_ausentes_cadastro) > 0) {
  warning("Há códigos da classificação ausentes do Ses_ramos atual.")
}
if (nrow(codigos_cadastro_ausentes_classificacao) > 0) {
  warning("O Ses_ramos atual contém códigos novos não presentes na revisão.")
}


cadastro_classificado <- ses_ramos %>%
  select(coramo, noramo) %>%
  left_join(classificacao_revisada, by = "coramo") %>%
  mutate(
    cenario_amplo_revisado = replace_na(cenario_amplo_revisado, FALSE),
    cenario_conservador_revisado =
      replace_na(cenario_conservador_revisado, FALSE),
    categoria_projeto_revisada =
      replace_na(categoria_projeto_revisada, "fora_escopo")
  )


numero_linhas_antes <- nrow(ses_seguros)
seguros_final <- ses_seguros %>%
  left_join(cadastro_classificado, by = "coramo")
numero_linhas_depois <- nrow(seguros_final)


teste_join <- tibble(
  etapa = c("antes_do_join", "depois_do_join"),
  linhas = c(numero_linhas_antes, numero_linhas_depois)
)
if (numero_linhas_antes != numero_linhas_depois) {
  stop("A junção alterou o número de linhas da base operacional.")
}


seguros_2010_2025 <- seguros_final %>%
  filter(between(ano, 2010, 2025))


# ============================================================
# 6. CONTROLES DE COBERTURA E CORRESPONDÊNCIA
# ============================================================


cobertura_mensal <- seguros_2010_2025 %>%
  group_by(ano) %>%
  summarise(
    meses_disponiveis = n_distinct(mes),
    primeiro_mes = min(mes),
    ultimo_mes = max(mes),
    lista_meses = paste(sort(unique(mes)), collapse = ", "),
    .groups = "drop"
  ) %>%
  arrange(ano)


if (
  nrow(cobertura_mensal) != 16 ||
  any(cobertura_mensal$meses_disponiveis != 12) ||
  any(cobertura_mensal$primeiro_mes != 1) ||
  any(cobertura_mensal$ultimo_mes != 12)
) warning("Há anos incompletos entre 2010 e 2025.")


codigos_operacionais_sem_cadastro <- seguros_2010_2025 %>%
  filter(is.na(noramo)) %>%
  group_by(ano, coramo) %>%
  summarise(
    registros = n(),
    premio_direto = soma_segura(premio_direto),
    .groups = "drop"
  )


ramos_incluidos_sem_dados <- classificacao_revisada %>%
  filter(cenario_amplo_revisado) %>%
  anti_join(
    seguros_2010_2025 %>% distinct(coramo),
    by = "coramo"
  )


# ============================================================
# 7. CLASSIFICAÇÃO ORIGINAL PARA COMPARAÇÃO
# ============================================================


ramos_amplo_original <- c(
  531, 542, 553, 524, 525, 527,
  111, 114, 116, 117, 118, 141, 142, 143, 167, 171, 176, 195, 196,
  621, 622, 623, 628, 632, 638, 652, 654, 655, 656, 658, 659
)
ramos_conservador_original <- c(
  531, 114, 116, 117, 118, 621, 622, 654, 655
)


seguros_2010_2025 <- seguros_2010_2025 %>%
  mutate(
    cenario_amplo_original = coramo %in% ramos_amplo_original,
    cenario_conservador_original = coramo %in% ramos_conservador_original
  )


mudancas_classificacao <- cadastro_classificado %>%
  transmute(
    coramo,
    noramo,
    categoria_projeto_revisada,
    amplo_original = coramo %in% ramos_amplo_original,
    amplo_revisado = cenario_amplo_revisado,
    mudanca_amplo = case_when(
      !amplo_original & amplo_revisado ~ "adicionado",
      amplo_original & !amplo_revisado ~ "removido",
      TRUE ~ "sem_mudanca"
    ),
    conservador_original = coramo %in% ramos_conservador_original,
    conservador_revisado = cenario_conservador_revisado,
    mudanca_conservador = case_when(
      !conservador_original & conservador_revisado ~ "adicionado",
      conservador_original & !conservador_revisado ~ "removido",
      TRUE ~ "sem_mudanca"
    )
  ) %>%
  filter(mudanca_amplo != "sem_mudanca" |
           mudanca_conservador != "sem_mudanca") %>%
  arrange(coramo)


# ============================================================
# 8. AUDITORIA POR RAMO E POR MÊS
# ============================================================


auditoria_por_ramo <- seguros_2010_2025 %>%
  filter(cenario_amplo_revisado | cenario_conservador_revisado) %>%
  group_by(
    ano, coramo, noramo, categoria_projeto_revisada,
    cenario_amplo_revisado, cenario_conservador_revisado
  ) %>%
  summarise(
    registros = n(),
    premio_direto_valido = sum(!is.na(premio_direto)),
    premio_direto_ausente = sum(is.na(premio_direto)),
    premio_direto = soma_segura(premio_direto),
    premio_ganho = soma_segura(premio_ganho),
    .groups = "drop"
  ) %>%
  arrange(ano, categoria_projeto_revisada, coramo)


auditoria_mensal_2025 <- seguros_2010_2025 %>%
  filter(ano == 2025, cenario_amplo_revisado) %>%
  group_by(
    mes, coramo, noramo, categoria_projeto_revisada,
    cenario_amplo_revisado, cenario_conservador_revisado
  ) %>%
  summarise(
    registros = n(),
    premio_direto = soma_segura(premio_direto),
    premio_ganho = soma_segura(premio_ganho),
    .groups = "drop"
  ) %>%
  arrange(coramo, mes)


# ============================================================
# 9. CALCULAR OS CENÁRIOS REVISADOS
# ============================================================


calcular_composicao <- function(base, coluna_cenario, nome_cenario) {
  base %>%
    filter(.data[[coluna_cenario]]) %>%
    group_by(ano, categoria_projeto_revisada) %>%
    summarise(
      premio_direto = soma_segura(premio_direto),
      premio_ganho = soma_segura(premio_ganho),
      .groups = "drop"
    ) %>%
    group_by(ano) %>%
    mutate(
      premio_direto_total_ano = sum(premio_direto, na.rm = TRUE),
      proporcao_premio_direto = premio_direto / premio_direto_total_ano,
      cenario = nome_cenario
    ) %>%
    ungroup()
}


composicao_revisada <- bind_rows(
  calcular_composicao(
    seguros_2010_2025, "cenario_amplo_revisado", "amplo"
  ),
  calcular_composicao(
    seguros_2010_2025, "cenario_conservador_revisado", "conservador"
  )
) %>%
  arrange(cenario, ano, categoria_projeto_revisada)


serie_total_revisada <- composicao_revisada %>%
  distinct(cenario, ano, premio_direto_total_ano) %>%
  arrange(cenario, ano)


serie_por_grupo_revisada <- composicao_revisada %>%
  select(
    cenario, ano, categoria_projeto_revisada, premio_direto
  ) %>%
  pivot_wider(
    names_from = categoria_projeto_revisada,
    values_from = premio_direto,
    values_fill = 0
  ) %>%
  mutate(
    gasto_total = rowSums(
      across(-c(cenario, ano)),
      na.rm = TRUE
    )
  ) %>%
  arrange(cenario, ano)


# ============================================================
# 10. COMPARAR CLASSIFICAÇÃO ORIGINAL E REVISADA
# ============================================================


calcular_total_simples <- function(base, coluna, rotulo) {
  base %>%
    filter(.data[[coluna]]) %>%
    group_by(ano) %>%
    summarise(valor = soma_segura(premio_direto), .groups = "drop") %>%
    mutate(serie = rotulo)
}


totais_comparacao_longos <- bind_rows(
  calcular_total_simples(
    seguros_2010_2025, "cenario_amplo_original", "amplo_original"
  ),
  calcular_total_simples(
    seguros_2010_2025, "cenario_amplo_revisado", "amplo_revisado"
  ),
  calcular_total_simples(
    seguros_2010_2025, "cenario_conservador_original", "conservador_original"
  ),
  calcular_total_simples(
    seguros_2010_2025, "cenario_conservador_revisado", "conservador_revisado"
  )
)


impacto_revisao <- totais_comparacao_longos %>%
  pivot_wider(names_from = serie, values_from = valor) %>%
  mutate(
    diferenca_amplo = amplo_revisado - amplo_original,
    variacao_percentual_amplo = diferenca_amplo / amplo_original,
    diferenca_conservador = conservador_revisado - conservador_original,
    variacao_percentual_conservador =
      diferenca_conservador / conservador_original
  ) %>%
  arrange(ano)


impacto_por_ramo <- seguros_2010_2025 %>%
  filter(
    coramo %in% mudancas_classificacao$coramo
  ) %>%
  group_by(ano, coramo, noramo) %>%
  summarise(
    premio_direto = soma_segura(premio_direto),
    .groups = "drop"
  ) %>%
  left_join(
    mudancas_classificacao,
    by = c("coramo", "noramo")
  ) %>%
  arrange(ano, coramo)


# ============================================================
# 11. COMPARAR PRÊMIO DIRETO E PRÊMIO GANHO
# ============================================================


comparacao_premios <- seguros_2010_2025 %>%
  filter(cenario_amplo_revisado) %>%
  group_by(ano) %>%
  summarise(
    premio_direto = soma_segura(premio_direto),
    premio_ganho = soma_segura(premio_ganho),
    diferenca = premio_direto - premio_ganho,
    premio_ganho_sobre_direto = premio_ganho / premio_direto,
    .groups = "drop"
  )


# ============================================================
# 12. TESTES DE RECONCILIAÇÃO
# ============================================================


teste_somas <- composicao_revisada %>%
  group_by(cenario, ano) %>%
  summarise(
    soma_grupos = sum(premio_direto, na.rm = TRUE),
    total_registrado = first(premio_direto_total_ano),
    diferenca = soma_grupos - total_registrado,
    .groups = "drop"
  )


if (any(abs(teste_somas$diferenca) > 0.01)) {
  stop("As somas por grupo não reconciliam com os totais anuais.")
}


if (any(auditoria_por_ramo$premio_direto_ausente > 0)) {
  warning("Existem registros selecionados com prêmio direto ausente.")
}


print(
  serie_por_grupo_revisada %>%
    filter(ano == 2025)
)
print(
  impacto_revisao %>%
    filter(ano == 2025)
)


# ============================================================
# 13. EXPORTAR PLANILHA AUDITÁVEL
# ============================================================


write_xlsx(
  list(
    serie_total_revisada = serie_total_revisada,
    serie_por_grupo_revisada = serie_por_grupo_revisada,
    composicao_revisada = composicao_revisada,
    impacto_revisao = impacto_revisao,
    impacto_por_ramo = impacto_por_ramo,
    mudancas_classificacao = mudancas_classificacao,
    auditoria_por_ramo = auditoria_por_ramo,
    auditoria_mensal_2025 = auditoria_mensal_2025,
    classificacao_revisada = classificacao_revisada,
    comparacao_premios = comparacao_premios,
    cobertura_mensal = cobertura_mensal,
    teste_somas = teste_somas,
    teste_join = teste_join,
    ramos_incluidos_sem_dados = ramos_incluidos_sem_dados,
    codigos_operacionais_sem_cadastro = codigos_operacionais_sem_cadastro,
    codigos_novos_no_cadastro = codigos_cadastro_ausentes_classificacao,
    codigos_classif_ausentes = codigos_classificacao_ausentes_cadastro
  ),
  arquivo_saida
)


message("Arquivo criado em: ", arquivo_saida)








# ============================================================================
# PERDAS PATRIMONIAIS E DE CARGA — SUSEP/SES (2010–2025)
# Classificação revisada e regra de transição auditada
# ============================================================================
#
# DEFINIÇÕES METODOLÓGICAS
# 1. Janeiro/2010 a novembro/2013: sinistro_direto.
# 2. Dezembro/2013 a dezembro/2025: sinistro_ocorrido.
# 3. A mudança é mensal e ocorre em 201312, não na virada 2013/2014.
# 4. Valores negativos são preservados (estornos, recuperações e ajustes).
# 5. Há dois cenários aninhados: conservador contido no amplo.
# 6. O arquivo exportado contém valores NOMINAIS. A atualização monetária
#    deve ser feita depois com o fator anual para dezembro de 2025.


# ============================================================================
# 1. CAMINHOS
# ============================================================================


pasta_base <- dir_susep
pasta_saida <- dir_saida


arquivo_ramos <- file.path(pasta_base, "Ses_ramos.csv")
arquivo_seguros <- file.path(pasta_base, "Ses_seguros.csv")


arquivo_saida <- file.path(
  pasta_saida,
  "resultados_perdas_patrimoniais_carga_2010_2025_classificacao_revisada.xlsx"
)


if (!file.exists(arquivo_ramos)) stop("Ses_ramos.csv não encontrado.")
if (!file.exists(arquivo_seguros)) stop("Ses_seguros.csv não encontrado.")


# ============================================================================
# 2. FUNÇÕES AUXILIARES
# ============================================================================


converter_numero <- function(x) {
  if (is.numeric(x)) return(as.numeric(x))
  
  x <- trimws(as.character(x))
  x[x %in% c("", "NA", "N/A", "...", "-")] <- NA_character_
  possui_virgula <- grepl(",", x, fixed = TRUE)
  resultado <- rep(NA_real_, length(x))
  
  resultado[possui_virgula] <- as.numeric(
    gsub(
      ",", ".",
      gsub(".", "", x[possui_virgula], fixed = TRUE),
      fixed = TRUE
    )
  )
  resultado[!possui_virgula] <- as.numeric(x[!possui_virgula])
  resultado
}


soma_segura <- function(x) {
  if (all(is.na(x))) NA_real_ else sum(x, na.rm = TRUE)
}


# ============================================================================
# 3. CLASSIFICAÇÃO DEFINITIVA DOS RAMOS
# ============================================================================
# A classificação abaixo é própria para PERDAS MATERIAIS. Ela não deve ser
# confundida com a classificação dos prêmios usada em gastos com seguros.


classificacao_perdas <- tribble(
  ~coramo, ~categoria_projeto, ~cenario_amplo, ~cenario_conservador, ~decisao_metodologica,
  111, "patrimonial", TRUE,  FALSE, "Incêndio tradicional (run-off); cobertura material, mas não específica a crime.",
  114, "patrimonial", TRUE,  TRUE,  "Compreensivo residencial; inclui bens materiais e cobertura relevante a subtração.",
  115, "patrimonial", TRUE,  TRUE,  "Roubo (run-off); relação direta com subtração de patrimônio.",
  116, "patrimonial", TRUE,  TRUE,  "Compreensivo condomínio; inclui danos e subtração de bens materiais.",
  117, "patrimonial", TRUE,  FALSE, "Tumultos; pode cobrir dano material ligado a ação humana, mas é modalidade ampla.",
  118, "patrimonial", TRUE,  TRUE,  "Compreensivo empresarial; inclui danos e subtração de bens materiais.",
  141, "patrimonial", FALSE, FALSE, "Lucros cessantes; perda de rendimento, não perda material.",
  142, "patrimonial", FALSE, FALSE, "Lucros cessantes cobertura simples; perda de rendimento e sem registros no período.",
  143, "patrimonial", FALSE, FALSE, "Fidelidade; perda predominantemente financeira e sem registros no período.",
  167, "patrimonial", TRUE,  FALSE, "Riscos de engenharia; perda material possível, mas relação com crime não específica.",
  171, "patrimonial", TRUE,  FALSE, "Riscos diversos; contém perdas materiais, porém é heterogêneo.",
  173, "patrimonial", TRUE,  FALSE, "Global de bancos; pode incluir subtração material, mas agrega coberturas heterogêneas.",
  176, "patrimonial", TRUE,  FALSE, "Riscos diversos — planos conjugados; cobertura material heterogênea.",
  196, "patrimonial", TRUE,  FALSE, "Riscos nomeados e operacionais; pode incluir dano material, mas não apenas criminal.",
  621, "transporte_carga", TRUE, TRUE,  "Transporte nacional; perdas indenizadas de mercadorias transportadas.",
  622, "transporte_carga", TRUE, TRUE,  "Transporte internacional; perdas indenizadas de mercadorias transportadas.",
  627, "transporte_carga", TRUE, FALSE, "Transporte em modalidade específica; perda de carga possível, mas cobertura ampla.",
  632, "transporte_carga", TRUE, FALSE, "Responsabilidade civil do transportador; pode incluir perda de carga, mas não apenas crime.",
  638, "transporte_carga", TRUE, FALSE, "Responsabilidade do transportador em modalidade específica; cobertura ampla.",
  652, "transporte_carga", TRUE, FALSE, "Responsabilidade civil ligada à carga; cobertura não delimitada a subtração.",
  654, "transporte_carga", TRUE, FALSE, "RCTR-C; cobre responsabilidades de transporte, inclusive eventos não criminais.",
  655, "transporte_carga", TRUE, TRUE,  "Responsabilidade civil por desaparecimento de carga; relação direta com subtração.",
  656, "transporte_carga", TRUE, FALSE, "Responsabilidade civil ligada ao transporte; modalidade mais ampla que desaparecimento.",
  658, "transporte_carga", TRUE, FALSE, "Responsabilidade civil ligada à carga; inclui riscos não exclusivamente criminais."
)


# Testes da matriz classificatória.
if (anyDuplicated(classificacao_perdas$coramo) > 0) {
  stop("Há códigos duplicados na classificação de perdas.")
}


if (any(classificacao_perdas$cenario_conservador &
        !classificacao_perdas$cenario_amplo)) {
  stop("O cenário conservador deve estar integralmente contido no amplo.")
}


if (sum(classificacao_perdas$cenario_amplo) != 21) {
  stop("O cenário amplo deveria conter 21 ramos: 11 patrimoniais e 10 de carga.")
}


if (sum(classificacao_perdas$cenario_conservador) != 7) {
  stop("O cenário conservador deveria conter 7 ramos: 4 patrimoniais e 3 de carga.")
}


# ============================================================================
# 4. IMPORTAÇÃO E VALIDAÇÃO DAS BASES
# ============================================================================


ses_ramos <- fread(
  arquivo_ramos,
  sep = ";",
  encoding = "Latin-1"
)


ses_seguros <- fread(
  arquivo_seguros,
  sep = ";",
  encoding = "Latin-1"
)


colunas_ramos_necessarias <- c("coramo", "noramo")
colunas_seguros_necessarias <- c(
  "damesano", "coramo",
  "sinistro_direto", "sinistro_retido", "sinistro_ocorrido"
)


if (!all(colunas_ramos_necessarias %in% names(ses_ramos))) {
  stop("Ses_ramos.csv não contém coramo e noramo.")
}


if (!all(colunas_seguros_necessarias %in% names(ses_seguros))) {
  stop(
    paste0(
      "Ses_seguros.csv não contém: ",
      paste(
        setdiff(colunas_seguros_necessarias, names(ses_seguros)),
        collapse = ", "
      )
    )
  )
}


duplicacoes_cadastro <- ses_ramos %>%
  count(coramo, sort = TRUE) %>%
  filter(n > 1)


if (nrow(duplicacoes_cadastro) > 0) {
  stop("Ses_ramos.csv possui códigos coramo duplicados.")
}


ses_seguros[
  ,
  c("sinistro_direto", "sinistro_retido", "sinistro_ocorrido") :=
    lapply(.SD, converter_numero),
  .SDcols = c("sinistro_direto", "sinistro_retido", "sinistro_ocorrido")
]


ses_seguros <- ses_seguros %>%
  mutate(
    damesano = as.integer(damesano),
    coramo = as.integer(coramo),
    ano = floor(damesano / 100),
    mes = damesano %% 100
  )


if (any(!ses_seguros$mes %in% 1:12, na.rm = TRUE)) {
  stop("Há valores inválidos de mês derivados de damesano.")
}


cadastro_classificado <- classificacao_perdas %>%
  left_join(
    ses_ramos %>% select(coramo, noramo),
    by = "coramo"
  ) %>%
  relocate(noramo, .after = coramo)


codigos_sem_cadastro <- cadastro_classificado %>%
  filter(is.na(noramo))


if (nrow(codigos_sem_cadastro) > 0) {
  stop(
    paste0(
      "Códigos da classificação ausentes em Ses_ramos.csv: ",
      paste(codigos_sem_cadastro$coramo, collapse = ", ")
    )
  )
}


# ============================================================================
# 5. JUNÇÃO, FILTRO TEMPORAL E VARIÁVEL HÍBRIDA
# ============================================================================


numero_linhas_base_completa <- nrow(ses_seguros)


base_periodo <- ses_seguros %>%
  filter(between(ano, 2010, 2025))


numero_linhas_periodo_antes_join <- nrow(base_periodo)


base_classificada <- base_periodo %>%
  left_join(cadastro_classificado, by = "coramo")


numero_linhas_periodo_depois_join <- nrow(base_classificada)


if (numero_linhas_periodo_antes_join != numero_linhas_periodo_depois_join) {
  stop("A junção alterou o número de registros da base no período.")
}


base_perdas <- base_classificada %>%
  filter(!is.na(categoria_projeto)) %>%
  mutate(
    fonte_sinistro = case_when(
      damesano <= 201311 ~ "sinistro_direto",
      damesano >= 201312 ~ "sinistro_ocorrido",
      TRUE ~ NA_character_
    ),
    sinistro_hibrido = case_when(
      damesano <= 201311 ~ sinistro_direto,
      damesano >= 201312 ~ sinistro_ocorrido,
      TRUE ~ NA_real_
    )
  )


if (any(is.na(base_perdas$sinistro_hibrido))) {
  warning(
    paste0(
      "Há ", sum(is.na(base_perdas$sinistro_hibrido)),
      " registros candidatos com sinistro_hibrido ausente. Consulte a aba de controle."
    )
  )
}


# ============================================================================
# 6. DETALHAMENTO ANUAL POR RAMO
# ============================================================================


detalhamento_anual_ramo <- base_perdas %>%
  group_by(
    ano, coramo, noramo, categoria_projeto,
    cenario_amplo, cenario_conservador
  ) %>%
  summarise(
    registros = n(),
    meses_com_registros = n_distinct(damesano),
    valores_ausentes = sum(is.na(sinistro_hibrido)),
    valores_negativos = sum(sinistro_hibrido < 0, na.rm = TRUE),
    perda_nominal = soma_segura(sinistro_hibrido),
    .groups = "drop"
  ) %>%
  arrange(ano, categoria_projeto, coramo)


# ============================================================================
# 7. SÉRIES NOMINAIS POR CENÁRIO E CATEGORIA
# ============================================================================


serie_categoria_cenario <- bind_rows(
  base_perdas %>%
    filter(cenario_amplo) %>%
    mutate(cenario = "amplo"),
  base_perdas %>%
    filter(cenario_conservador) %>%
    mutate(cenario = "conservador")
) %>%
  group_by(ano, cenario, categoria_projeto) %>%
  summarise(
    perda_nominal = soma_segura(sinistro_hibrido),
    .groups = "drop"
  ) %>%
  complete(
    ano = 2010:2025,
    cenario = c("amplo", "conservador"),
    categoria_projeto = c("patrimonial", "transporte_carga"),
    fill = list(perda_nominal = 0)
  ) %>%
  arrange(cenario, ano, categoria_projeto)


serie_final_nominal <- serie_categoria_cenario %>%
  pivot_wider(
    names_from = categoria_projeto,
    values_from = perda_nominal
  ) %>%
  mutate(
    perdas_patrimoniais_nominais = patrimonial,
    perdas_carga_nominais = transporte_carga,
    perdas_patrimoniais_carga_nominais =
      perdas_patrimoniais_nominais + perdas_carga_nominais
  ) %>%
  select(
    ano,
    cenario,
    perdas_patrimoniais_nominais,
    perdas_carga_nominais,
    perdas_patrimoniais_carga_nominais
  ) %>%
  arrange(cenario, ano)


# ============================================================================
# 8. CONTROLES DA TRANSIÇÃO E DA QUALIDADE DOS DADOS
# ============================================================================


controle_transicao_mensal <- base_perdas %>%
  filter(between(damesano, 201201, 201412)) %>%
  group_by(damesano, ano, mes) %>%
  summarise(
    sinistro_direto = soma_segura(sinistro_direto),
    sinistro_retido = soma_segura(sinistro_retido),
    sinistro_ocorrido = soma_segura(sinistro_ocorrido),
    sinistro_hibrido = soma_segura(sinistro_hibrido),
    fonte_sinistro = first(fonte_sinistro),
    .groups = "drop"
  ) %>%
  arrange(damesano)


controle_qualidade_anual <- base_perdas %>%
  group_by(ano, categoria_projeto) %>%
  summarise(
    registros = n(),
    meses_com_registros = n_distinct(damesano),
    codigos_com_registros = n_distinct(coramo),
    hibrido_ausente = sum(is.na(sinistro_hibrido)),
    hibrido_zero = sum(sinistro_hibrido == 0, na.rm = TRUE),
    hibrido_positivo = sum(sinistro_hibrido > 0, na.rm = TRUE),
    hibrido_negativo = sum(sinistro_hibrido < 0, na.rm = TRUE),
    soma_hibrido = soma_segura(sinistro_hibrido),
    .groups = "drop"
  ) %>%
  arrange(ano, categoria_projeto)


codigos_sem_dados <- cadastro_classificado %>%
  anti_join(
    base_perdas %>% distinct(coramo),
    by = "coramo"
  ) %>%
  select(coramo, noramo, categoria_projeto, cenario_amplo,
         cenario_conservador, decisao_metodologica)


# Reconciliação: soma das categorias deve coincidir exatamente com o total.
reconciliacao <- serie_categoria_cenario %>%
  group_by(ano, cenario) %>%
  summarise(
    soma_categorias = sum(perda_nominal, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  left_join(
    serie_final_nominal %>%
      select(
        ano,
        cenario,
        total_final = perdas_patrimoniais_carga_nominais
      ),
    by = c("ano", "cenario")
  ) %>%
  mutate(
    diferenca = total_final - soma_categorias,
    reconciliado = abs(diferenca) < 0.01
  )


if (any(!reconciliacao$reconciliado)) {
  stop("Os totais finais não reconciliam com a soma das categorias.")
}


# Controle explícito de cobertura anual e mensal da base selecionada.
cobertura_calendario <- base_perdas %>%
  group_by(ano) %>%
  summarise(
    meses_distintos = n_distinct(mes),
    primeiro_mes = min(mes),
    ultimo_mes = max(mes),
    .groups = "drop"
  ) %>%
  complete(
    ano = 2010:2025,
    fill = list(meses_distintos = 0L)
  ) %>%
  mutate(
    cobertura_12_meses = coalesce(
      meses_distintos == 12 & primeiro_mes == 1 & ultimo_mes == 12,
      FALSE
    )
  )


if (any(!cobertura_calendario$cobertura_12_meses)) {
  warning("Nem todos os anos possuem registros nos 12 meses. Consulte cobertura_calendario.")
}


resumo_execucao <- tibble(
  verificacao = c(
    "Registros na base completa",
    "Registros de 2010 a 2025 antes do join",
    "Registros de 2010 a 2025 depois do join",
    "Ramos avaliados",
    "Ramos no cenário amplo",
    "Ramos no cenário conservador",
    "Ramos sem registros no período",
    "Início da fonte sinistro_direto",
    "Fim da fonte sinistro_direto",
    "Início da fonte sinistro_ocorrido",
    "Fim da fonte sinistro_ocorrido",
    "Todas as reconciliações aprovadas"
  ),
  valor = as.character(c(
    numero_linhas_base_completa,
    numero_linhas_periodo_antes_join,
    numero_linhas_periodo_depois_join,
    nrow(classificacao_perdas),
    sum(classificacao_perdas$cenario_amplo),
    sum(classificacao_perdas$cenario_conservador),
    nrow(codigos_sem_dados),
    "201001",
    "201311",
    "201312",
    "202512",
    all(reconciliacao$reconciliado)
  ))
)


# ============================================================================
# 9. MODELO PARA DEFLAÇÃO POSTERIOR
# ============================================================================
# A coluna fator_correcao_dez_2025 deve ser preenchida com os fatores anuais
# da aba "Indicadores Brasil" da planilha consolidada. As colunas deflacionadas
# são intencionalmente deixadas em branco para evitar usar fatores externos ou
# diferentes daqueles já adotados no projeto.


modelo_deflacao <- serie_final_nominal %>%
  mutate(
    fator_correcao_dez_2025 = NA_real_,
    perdas_patrimoniais_deflacionadas = NA_real_,
    perdas_carga_deflacionadas = NA_real_,
    perdas_patrimoniais_carga_deflacionadas = NA_real_
  )


# ============================================================================
# 10. EXPORTAÇÃO
# ============================================================================


abas_saida <- list(
  serie_final_nominal = serie_final_nominal,
  modelo_deflacao = modelo_deflacao,
  serie_categoria = serie_categoria_cenario,
  detalhe_anual_ramo = detalhamento_anual_ramo,
  classificacao_ramos = cadastro_classificado,
  transicao_2012_2014 = controle_transicao_mensal,
  qualidade_anual = controle_qualidade_anual,
  cobertura_calendario = cobertura_calendario,
  codigos_sem_dados = codigos_sem_dados,
  reconciliacao = reconciliacao,
  resumo_execucao = resumo_execucao
)


write_xlsx(abas_saida, arquivo_saida)


message("Processamento concluído.")
message("Arquivo salvo em: ", arquivo_saida)
