# ==============================================================================
# 03 — PERDAS PRODUTIVAS
# Projeto: Custos da Criminalidade no Brasil, 1996-2025
# ==============================================================================
# Escopo deste arquivo
# Reproduz as etapas em R: perfil de renda/ocupação na PNAD Contínua 2025, seleção dos registros do SIM, valores presentes e agregação anual. Usa VD4019, VD4002 e CO2 conforme a metodologia final; o SIM é separado em DOEXT (1996-2000) e DO (2001-2025).
#
# Reprodutibilidade
# 1. Ajuste somente os caminhos em "CONFIGURACAO".
# 2. Instale previamente os pacotes listados; o script não instala pacotes.
# 3. As etapas feitas em Excel são identificadas e não são recriadas aqui.
# 4. As saídas são gravadas em dir_saida sem chamadas interativas.
# ==============================================================================


options(stringsAsFactors = FALSE, survey.lonely.psu = "adjust")


# CONFIGURACAO ---------------------------------------------------------------
dir_saida <- "resultados/perdas_produtivas"
arquivo_tabua_mortalidade <- "dados/tabua_mortalidade.csv"
dir.create(dir_saida, recursive = TRUE, showWarnings = FALSE)


pacotes <- c("PNADcIBGE","survey","microdatasus","dplyr","stringr","purrr",
             "tidyr","tibble","writexl","ggplot2","scales")
faltantes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]
if (length(faltantes)) stop("Instale os pacotes: ", paste(faltantes, collapse = ", "))




options(survey.lonely.psu = "adjust")


imprimir_completo <- function(x) {
  print(tibble::as_tibble(x), n = Inf, width = Inf)
  invisible(x)
}


# ======================================================================
# 1. PARAMETROS
# ======================================================================


ano_pnadc <- 2025
ano_inicio <- 1996
ano_fim <- 2025
idade_inicio_renda <- 14
idade_agregacao_pnadc <- 70
idade_final_fluxo <- 90
taxa_crescimento_renda <- 0.02
taxa_desconto <- 0.03


regioes <- c("Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste")
pasta_saida <- dir_saida
dir.create(pasta_saida, showWarnings = FALSE, recursive = TRUE)


# ======================================================================
# 2. PNAD CONTINUA: RENDA ESPERADA POR IDADE E REGIAO
# ======================================================================


pnadc25 <- PNADcIBGE::get_pnadc(
  year = ano_pnadc,
  interview = 1,
  labels = FALSE,
  deflator = TRUE,
  design = TRUE
)


pnadc25 <- update(
  pnadc25,
  regiao = ifelse(UF >= 11 & UF <= 17, "Norte",
                  ifelse(UF >= 21 & UF <= 29, "Nordeste",
                         ifelse(UF >= 31 & UF <= 35, "Sudeste",
                                ifelse(UF >= 41 & UF <= 43, "Sul",
                                       ifelse(UF >= 50 & UF <= 53, "Centro-Oeste", NA)))))
)


pnadc25 <- update(
  pnadc25,
  idade_grupo = ifelse(V2009 >= idade_agregacao_pnadc,
                       idade_agregacao_pnadc, V2009),
  renda_total = suppressWarnings(as.numeric(VD4019)),
)


pnadc25 <- update(
  pnadc25,
  ocupado = ifelse(VD4002 == 1, 1, ifelse(VD4002 == 2, 0, NA))
)


renda_pnadc <- svyby(
  ~renda_total,
  ~idade_grupo + regiao,
  design = subset(
    pnadc25,
    ocupado == 1 & V2009 >= idade_inicio_renda & V2009 <= idade_final_fluxo
  ),
  FUN = svymean,
  na.rm = TRUE,
  vartype = "se"
)


ocupacao_pnadc <- svyby(
  ~ocupado,
  ~idade_grupo + regiao,
  design = subset(
    pnadc25,
    !is.na(ocupado) & V2009 >= idade_inicio_renda & V2009 <= idade_final_fluxo
  ),
  FUN = svymean,
  na.rm = TRUE,
  vartype = "se"
)


base_pnadc <- full_join(
  renda_pnadc %>%
    transmute(
      idade = as.numeric(idade_grupo), regiao = as.character(regiao),
      renda_media = as.numeric(renda_total), se_renda = as.numeric(se)
    ),
  ocupacao_pnadc %>%
    transmute(
      idade = as.numeric(idade_grupo), regiao = as.character(regiao),
      prob_ocupacao = as.numeric(ocupado), se_ocupacao = as.numeric(se)
    ),
  by = c("idade", "regiao")
) %>%
  mutate(
    idade_label = ifelse(idade == idade_agregacao_pnadc, "70+", as.character(idade)),
    renda_esperada = renda_media * prob_ocupacao
  ) %>%
  arrange(regiao, idade)


base_renda <- base_pnadc %>%
  transmute(
    idade = as.numeric(idade),
    regiao = str_trim(as.character(regiao)),
    renda_esperada = as.numeric(renda_esperada)
  ) %>%
  filter(
    regiao %in% regioes,
    idade >= idade_inicio_renda,
    idade <= idade_agregacao_pnadc
  )


duplicidades_renda <- base_renda %>% count(regiao, idade) %>% filter(n > 1)
if (nrow(duplicidades_renda) > 0) {
  imprimir_completo(duplicidades_renda)
  stop("Existem duplicidades de regiao x idade em base_pnadc.")
}


teste_cobertura_renda <- expand_grid(
  regiao = regioes,
  idade = idade_inicio_renda:idade_agregacao_pnadc
) %>%
  left_join(base_renda, by = c("regiao", "idade"))


diagnostico_renda <- teste_cobertura_renda %>%
  summarise(
    linhas = n(),
    renda_ausente = sum(is.na(renda_esperada)),
    renda_negativa = sum(renda_esperada < 0, na.rm = TRUE)
  )


if (anyNA(teste_cobertura_renda$renda_esperada)) {
  imprimir_completo(teste_cobertura_renda %>% filter(is.na(renda_esperada)))
  stop("Existem celulas de regiao x idade sem renda esperada.")
}
if (any(teste_cobertura_renda$renda_esperada < 0)) {
  stop("Foram encontrados valores negativos de renda esperada.")
}


grafico_renda_esperada <- ggplot(
  base_pnadc,
  aes(x = idade, y = renda_esperada, color = regiao, group = regiao)
) +
  geom_line(linewidth = 1.2, na.rm = TRUE) +
  scale_x_continuous(
    breaks = c(seq(15, 65, 5), 70),
    labels = c(seq(15, 65, 5), "70+")
  ) +
  scale_y_continuous(labels = label_number(big.mark = ".", decimal.mark = ",")) +
  labs(
    title = "Renda esperada do trabalho por idade e regiao",
    subtitle = "PNAD Continua 2025 - primeira entrevista",
    x = "Idade", y = "Renda esperada mensal (R$)", color = "Regiao"
  ) +
  theme_minimal(base_size = 14) +
  theme(legend.position = "bottom", plot.title = element_text(face = "bold"))


ggsave(
  file.path(pasta_saida, "renda_esperada_idade_regiao.png"),
  grafico_renda_esperada, width = 11, height = 7, dpi = 300
)


# ======================================================================
# 3. SIM: IDENTIFICAR HOMICIDIOS PELA CAUSA BASICA (CID-10)
# ======================================================================


dados <- dplyr::bind_rows(
  microdatasus::fetch_datasus(
    year_start = 1996, year_end = 2000, uf = "all",
    information_system = "SIM-DOEXT"
  ),
  microdatasus::fetch_datasus(
    year_start = 2001, year_end = 2025, uf = "all",
    information_system = "SIM-DO"
  )
)


variaveis_sim_necessarias <- c(
  "CAUSABAS", "CIRCOBITO", "DTOBITO", "IDADE", "CODMUNRES"
)
variaveis_sim_ausentes <- setdiff(variaveis_sim_necessarias, names(dados))
if (length(variaveis_sim_ausentes) > 0) {
  stop(paste("Variaveis ausentes no SIM:",
             paste(variaveis_sim_ausentes, collapse = ", ")))
}


dados_validacao <- dados %>%
  mutate(
    causa_basica = str_replace_all(
      toupper(str_trim(as.character(CAUSABAS))), "[^A-Z0-9]", ""
    ),
    categoria_cid = substr(causa_basica, 1, 3),
    homicidio_cid = !is.na(categoria_cid) &
      (between(categoria_cid, "X85", "X99") |
         between(categoria_cid, "Y00", "Y09") |
         categoria_cid %in% c("Y35", "Y36")),
    circobito_padronizado = str_trim(as.character(CIRCOBITO)),
    homicidio_circobito = !is.na(circobito_padronizado) &
      circobito_padronizado == "3",
    data_obito_codigo = str_pad(as.character(DTOBITO), 8, side = "left", pad = "0"),
    ano = suppressWarnings(as.numeric(substr(data_obito_codigo, 5, 8)))
  )


comparacao_criterios <- dados_validacao %>%
  filter(ano >= ano_inicio, ano <= ano_fim) %>%
  group_by(ano) %>%
  summarise(
    homicidios_cid = sum(homicidio_cid, na.rm = TRUE),
    homicidios_circobito = sum(homicidio_circobito, na.rm = TRUE),
    identificados_pelos_dois = sum(homicidio_cid & homicidio_circobito, na.rm = TRUE),
    somente_cid = sum(homicidio_cid & !homicidio_circobito, na.rm = TRUE),
    somente_circobito = sum(!homicidio_cid & homicidio_circobito, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    diferenca_cid_menos_circobito = homicidios_cid - homicidios_circobito,
    diferenca_percentual = 100 * diferenca_cid_menos_circobito / homicidios_cid,
    percentual_cid_coberto_por_circobito =
      100 * identificados_pelos_dois / homicidios_cid,
    teste_cid = homicidios_cid - (identificados_pelos_dois + somente_cid),
    teste_circobito = homicidios_circobito -
      (identificados_pelos_dois + somente_circobito)
  ) %>%
  arrange(ano)


if (any(comparacao_criterios$teste_cid != 0 |
        comparacao_criterios$teste_circobito != 0)) {
  stop("A decomposicao dos criterios CID-10 e CIRCOBITO nao fecha.")
}


dados_hom <- dados_validacao %>%
  filter(homicidio_cid) %>%
  mutate(
    idade_codigo = str_pad(as.character(IDADE), 3, side = "left", pad = "0"),
    unidade_idade = substr(idade_codigo, 1, 1),
    quantidade_idade = suppressWarnings(as.numeric(substr(idade_codigo, 2, 3))),
    idade_anos = case_when(
      unidade_idade %in% c("0", "1", "2", "3") ~ 0,
      unidade_idade == "4" ~ quantidade_idade,
      unidade_idade == "5" ~ 100 + quantidade_idade,
      TRUE ~ NA_real_
    ),
    codigo_municipio = str_pad(as.character(CODMUNRES), 6, side = "left", pad = "0"),
    uf = substr(codigo_municipio, 1, 2),
    regiao = case_when(
      uf %in% c("11", "12", "13", "14", "15", "16", "17") ~ "Norte",
      uf %in% c("21", "22", "23", "24", "25", "26", "27", "28", "29") ~ "Nordeste",
      uf %in% c("31", "32", "33", "35") ~ "Sudeste",
      uf %in% c("41", "42", "43") ~ "Sul",
      uf %in% c("50", "51", "52", "53") ~ "Centro-Oeste",
      TRUE ~ NA_character_
    )
  )


diagnostico_homicidios <- dados_hom %>%
  summarise(
    homicidios_identificados_cid = n(),
    ano_ausente = sum(is.na(ano)),
    idade_ausente = sum(is.na(idade_anos)),
    regiao_ausente = sum(is.na(regiao)),
    ano_minimo = min(ano, na.rm = TRUE),
    ano_maximo = max(ano, na.rm = TRUE),
    idade_minima = min(idade_anos, na.rm = TRUE),
    idade_maxima = max(idade_anos, na.rm = TRUE)
  )


diagnostico_unidade_idade <- dados_hom %>%
  count(unidade_idade, sort = TRUE, name = "homicidios")


diagnostico_idades <- dados_hom %>%
  count(idade_anos, name = "homicidios") %>% arrange(idade_anos)


diagnostico_ano <- dados_hom %>%
  count(ano, name = "homicidios") %>% arrange(ano)


base_homicidios <- dados_hom %>%
  filter(
    !is.na(ano), !is.na(idade_anos), !is.na(regiao),
    ano >= ano_inicio, ano <= ano_fim, idade_anos >= 0
  ) %>%
  mutate(idade = floor(idade_anos)) %>%
  count(ano, idade, regiao, name = "homicidios") %>%
  arrange(ano, regiao, idade)


diagnostico_exclusoes <- tibble(
  indicador = c(
    "Homicidios identificados pela CID-10",
    "Homicidios incluidos na base de calculo",
    "Homicidios excluidos por informacao ausente ou invalida"
  ),
  valor = c(
    nrow(dados_hom),
    sum(base_homicidios$homicidios),
    nrow(dados_hom) - sum(base_homicidios$homicidios)
  )
)


# ======================================================================
# 4. TABUA DE MORTALIDADE
# ======================================================================


caminho_tabua <- arquivo_tabua_mortalidade
if (!file.exists(caminho_tabua)) {
  stop(paste0("Tabua de mortalidade nao encontrada em: ", caminho_tabua))
}


tabua_original <- read.csv(
  caminho_tabua, check.names = FALSE, stringsAsFactors = FALSE
)
faltantes_tabua <- setdiff(c("idade", "lx"), names(tabua_original))
if (length(faltantes_tabua) > 0) {
  stop(paste("Variaveis ausentes na tabua:",
             paste(faltantes_tabua, collapse = ", ")))
}


tabua_mortalidade <- tabua_original %>%
  transmute(
    idade = suppressWarnings(as.numeric(str_extract(as.character(idade), "[0-9]+"))),
    lx = suppressWarnings(as.numeric(gsub(",", ".", str_trim(as.character(lx)),
                                          fixed = TRUE)))
  ) %>%
  filter(!is.na(idade), !is.na(lx), idade >= 0, idade <= idade_final_fluxo) %>%
  distinct(idade, .keep_all = TRUE) %>%
  arrange(idade)


teste_tabua <- tibble(idade = 0:idade_final_fluxo) %>%
  left_join(tabua_mortalidade, by = "idade")
if (anyNA(teste_tabua$lx) || any(teste_tabua$lx <= 0)) {
  imprimir_completo(teste_tabua %>% filter(is.na(lx) | lx <= 0))
  stop("A tabua precisa ter um lx positivo para cada idade entre 0 e 90.")
}
if (any(diff(teste_tabua$lx) > 0)) {
  stop("A coluna lx aumenta em alguma idade; revise a tabua de mortalidade.")
}


# ======================================================================
# 5. TRAJETORIA DE RENDA E VALORES PRESENTES
# ======================================================================


trajetoria_renda <- expand_grid(
  regiao = regioes,
  idade = idade_inicio_renda:idade_final_fluxo
) %>%
  mutate(idade_renda = pmin(idade, idade_agregacao_pnadc)) %>%
  left_join(
    base_renda %>% rename(idade_renda = idade),
    by = c("regiao", "idade_renda")
  ) %>%
  left_join(tabua_mortalidade, by = "idade") %>%
  arrange(regiao, idade)


if (nrow(trajetoria_renda) != length(regioes) *
    (idade_final_fluxo - idade_inicio_renda + 1)) {
  stop("Numero inesperado de linhas na trajetoria de renda.")
}
if (anyNA(trajetoria_renda$renda_esperada) || anyNA(trajetoria_renda$lx)) {
  imprimir_completo(trajetoria_renda %>%
                      filter(is.na(renda_esperada) | is.na(lx)))
  stop("Existem valores ausentes na trajetoria de renda.")
}


calcular_vp <- function(idade_inicial, regiao_ref,
                        g = taxa_crescimento_renda,
                        d = taxa_desconto) {
  if (length(idade_inicial) != 1 || is.na(idade_inicial) ||
      length(regiao_ref) != 1 || is.na(regiao_ref) ||
      !(regiao_ref %in% regioes)) return(NA_real_)
  if (g <= -1 || d <= -1) stop("As taxas g e d precisam ser superiores a -1.")
  if (idade_inicial >= idade_final_fluxo) return(0)
  
  lx_inicial <- tabua_mortalidade %>%
    filter(idade == idade_inicial) %>% pull(lx)
  if (length(lx_inicial) != 1 || is.na(lx_inicial) || lx_inicial <= 0) {
    return(NA_real_)
  }
  
  primeira_idade_fluxo <- max(idade_inicial + 1, idade_inicio_renda)
  traj <- trajetoria_renda %>%
    filter(
      regiao == regiao_ref,
      idade >= primeira_idade_fluxo,
      idade <= idade_final_fluxo
    ) %>%
    mutate(
      sobrevivencia = lx / lx_inicial,
      horizonte = idade - idade_inicial,
      renda_anual = renda_esperada * 12,
      valor_presente = renda_anual * sobrevivencia *
        ((1 + g)^horizonte) / ((1 + d)^horizonte)
    )
  sum(traj$valor_presente, na.rm = FALSE)
}


grid_vp <- expand_grid(regiao = regioes, idade = 0:idade_final_fluxo) %>%
  mutate(
    vp = map2_dbl(
      idade, regiao,
      ~ calcular_vp(.x, .y, taxa_crescimento_renda, taxa_desconto)
    )
  ) %>%
  arrange(regiao, idade)


diagnostico_grid_vp <- grid_vp %>%
  summarise(
    linhas = n(), vp_ausente = sum(is.na(vp)),
    vp_negativo = sum(vp < 0, na.rm = TRUE),
    vp_idade_90_diferente_zero = sum(
      idade == idade_final_fluxo & vp != 0, na.rm = TRUE
    )
  )


if (nrow(grid_vp) != length(regioes) * (idade_final_fluxo + 1)) {
  stop("Numero inesperado de linhas na grade de valores presentes.")
}
if (anyNA(grid_vp$vp) || any(grid_vp$vp < 0)) {
  imprimir_completo(grid_vp %>% filter(is.na(vp) | vp < 0))
  stop("Existem valores presentes ausentes ou negativos.")
}


diagnostico_variacao_vp <- grid_vp %>%
  group_by(regiao) %>%
  arrange(idade, .by_group = TRUE) %>%
  mutate(variacao_vp = vp - lag(vp)) %>%
  filter(variacao_vp > 0) %>%
  ungroup()


# ======================================================================
# 6. APLICAR O VP AOS HOMICIDIOS, IMPUTAR IDADES AUSENTES E AGREGAR
# ======================================================================


# ----------------------------------------------------------------------
# 6.1. PERDAS DOS HOMICIDIOS COM IDADE E REGIAO CONHECIDAS
# ----------------------------------------------------------------------


base_perdas <- base_homicidios %>%
  left_join(
    grid_vp,
    by = c("idade", "regiao")
  ) %>%
  mutate(
    # Vitimas com idade superior a 90 anos recebem VP igual a zero.
    # Para idades entre 0 e 90, o VP deve vir obrigatoriamente do grid_vp.
    vp = if_else(
      idade > idade_final_fluxo,
      0,
      vp
    ),
    perda_renda = homicidios * vp
  ) %>%
  arrange(
    ano,
    regiao,
    idade
  )


diagnostico_base_perdas <- base_perdas %>%
  summarise(
    linhas = n(),
    homicidios = sum(homicidios),
    vp_ausente = sum(is.na(vp)),
    perda_ausente = sum(is.na(perda_renda)),
    perda_negativa = sum(perda_renda < 0, na.rm = TRUE),
    homicidios_idade_maior_90 = sum(
      homicidios[idade > idade_final_fluxo],
      na.rm = TRUE
    ),
    homicidios_vp_zero = sum(
      homicidios[!is.na(vp) & vp == 0],
      na.rm = TRUE
    )
  )


if (
  anyNA(base_perdas$vp) ||
  anyNA(base_perdas$perda_renda)
) {
  imprimir_completo(
    base_perdas %>%
      filter(
        is.na(vp) |
          is.na(perda_renda)
      )
  )
  
  stop("Existem homicidios com idade conhecida sem valor presente correspondente.")
}


if (any(base_perdas$perda_renda < 0)) {
  stop("Existem perdas produtivas negativas.")
}


# ----------------------------------------------------------------------
# 6.2. RESULTADOS OBSERVADOS POR ANO E REGIAO
# ----------------------------------------------------------------------


perdas_ano_regiao <- base_perdas %>%
  group_by(
    ano,
    regiao
  ) %>%
  summarise(
    homicidios = sum(homicidios),
    perda_renda = sum(perda_renda),
    .groups = "drop"
  ) %>%
  complete(
    ano = ano_inicio:ano_fim,
    regiao = regioes,
    fill = list(
      homicidios = 0,
      perda_renda = 0
    )
  ) %>%
  arrange(
    ano,
    regiao
  )


perdas_brasil <- perdas_ano_regiao %>%
  group_by(ano) %>%
  summarise(
    homicidios = sum(homicidios),
    perda_renda = sum(perda_renda),
    .groups = "drop"
  ) %>%
  mutate(
    regiao = "Brasil",
    .after = ano
  )


teste_agregacao <- perdas_ano_regiao %>%
  group_by(ano) %>%
  summarise(
    homicidios_regioes = sum(homicidios),
    perda_regioes = sum(perda_renda),
    .groups = "drop"
  ) %>%
  left_join(
    perdas_brasil %>%
      transmute(
        ano,
        homicidios_brasil = homicidios,
        perda_brasil = perda_renda
      ),
    by = "ano"
  ) %>%
  mutate(
    diferenca_homicidios =
      homicidios_regioes -
      homicidios_brasil,
    
    diferenca_perda =
      perda_regioes -
      perda_brasil
  )


if (
  any(teste_agregacao$diferenca_homicidios != 0) ||
  any(abs(teste_agregacao$diferenca_perda) > 0.01)
) {
  stop("A soma dos resultados regionais difere do resultado nacional.")
}


perdas_consolidadas <- bind_rows(
  perdas_ano_regiao,
  perdas_brasil
) %>%
  arrange(
    ano,
    regiao
  )


# ----------------------------------------------------------------------
# 6.3. CLASSIFICAR HOMICIDIOS SEM IDADE UTILIZAVEL
# ----------------------------------------------------------------------


dados_hom_imputacao <- dados_hom %>%
  filter(
    !is.na(ano),
    ano >= ano_inicio,
    ano <= ano_fim
  ) %>%
  mutate(
    idade_conhecida =
      !is.na(idade_anos) &
      is.finite(idade_anos) &
      idade_anos >= 0,
    
    regiao_conhecida =
      !is.na(regiao) &
      str_trim(as.character(regiao)) != "" &
      regiao %in% regioes
  )


diagnostico_elegibilidade_imputacao <- dados_hom_imputacao %>%
  summarise(
    homicidios_identificados = n(),
    
    homicidios_idade_regiao_conhecidas = sum(
      idade_conhecida & regiao_conhecida,
      na.rm = TRUE
    ),
    
    homicidios_sem_idade_com_regiao = sum(
      !idade_conhecida & regiao_conhecida,
      na.rm = TRUE
    ),
    
    homicidios_com_idade_sem_regiao = sum(
      idade_conhecida & !regiao_conhecida,
      na.rm = TRUE
    ),
    
    homicidios_sem_idade_sem_regiao = sum(
      !idade_conhecida & !regiao_conhecida,
      na.rm = TRUE
    )
  ) %>%
  mutate(
    homicidios_sem_regiao =
      homicidios_com_idade_sem_regiao +
      homicidios_sem_idade_sem_regiao,
    
    soma_categorias =
      homicidios_idade_regiao_conhecidas +
      homicidios_sem_idade_com_regiao +
      homicidios_com_idade_sem_regiao +
      homicidios_sem_idade_sem_regiao,
    
    diferenca_decomposicao =
      homicidios_identificados -
      soma_categorias
  )


if (
  diagnostico_elegibilidade_imputacao$diferenca_decomposicao != 0
) {
  stop("A decomposicao dos casos elegiveis para imputacao nao fechou.")
}


if (
  diagnostico_elegibilidade_imputacao$homicidios_sem_regiao > 0
) {
  imprimir_completo(diagnostico_elegibilidade_imputacao)
  
  stop(
    paste0(
      "Foram encontrados homicidios sem regiao conhecida. ",
      "A regra atual imputa somente casos com regiao conhecida e idade ausente."
    )
  )
}


# ----------------------------------------------------------------------
# 6.4. CONTAR HOMICIDIOS SEM IDADE POR ANO E REGIAO
# ----------------------------------------------------------------------


homicidios_sem_idade_ano_regiao <- dados_hom_imputacao %>%
  filter(
    !idade_conhecida,
    regiao_conhecida
  ) %>%
  count(
    ano,
    regiao,
    name = "homicidios_sem_idade"
  ) %>%
  complete(
    ano = ano_inicio:ano_fim,
    regiao = regioes,
    fill = list(
      homicidios_sem_idade = 0
    )
  ) %>%
  arrange(
    ano,
    regiao
  )


# ----------------------------------------------------------------------
# 6.5. CALCULAR O VP MEDIO E A PERDA IMPUTADA
# ----------------------------------------------------------------------
#
# Para cada ano t e regiao r:
#
# vp_medio_observado[t,r] =
#   perda_observada[t,r] / homicidios_com_idade[t,r]
#
# perda_imputada[t,r] =
#   homicidios_sem_idade[t,r] * vp_medio_observado[t,r]
#
# ----------------------------------------------------------------------


perdas_imputadas <- perdas_ano_regiao %>%
  transmute(
    ano,
    regiao,
    
    homicidios_com_idade = homicidios,
    perda_observada = perda_renda
  ) %>%
  left_join(
    homicidios_sem_idade_ano_regiao,
    by = c("ano", "regiao")
  ) %>%
  mutate(
    vp_medio_observado = if_else(
      homicidios_com_idade > 0,
      perda_observada / homicidios_com_idade,
      NA_real_
    ),
    
    perda_imputada =
      homicidios_sem_idade *
      vp_medio_observado,
    
    homicidios_totais =
      homicidios_com_idade +
      homicidios_sem_idade,
    
    perda_total_com_imputacao =
      perda_observada +
      perda_imputada,
    
    percentual_homicidios_imputados = if_else(
      homicidios_totais > 0,
      100 * homicidios_sem_idade /
        homicidios_totais,
      0
    ),
    
    percentual_perda_imputada = if_else(
      perda_total_com_imputacao > 0,
      100 * perda_imputada /
        perda_total_com_imputacao,
      0
    )
  ) %>%
  arrange(
    ano,
    regiao
  )


# Uma celula com homicidios sem idade precisa ter VP medio observavel.


celulas_imputacao_sem_vp <- perdas_imputadas %>%
  filter(
    homicidios_sem_idade > 0,
    is.na(vp_medio_observado)
  )


if (nrow(celulas_imputacao_sem_vp) > 0) {
  imprimir_completo(celulas_imputacao_sem_vp)
  
  stop(
    paste0(
      "Existem celulas de ano e regiao com homicidios sem idade, ",
      "mas sem homicidios completos para calcular o VP medio."
    )
  )
}


# Nas celulas sem homicidios incompletos, uma eventual ausência do VP
# não altera a perda imputada. Ela é definida como zero.


perdas_imputadas <- perdas_imputadas %>%
  mutate(
    perda_imputada = if_else(
      homicidios_sem_idade == 0 &
        is.na(perda_imputada),
      0,
      perda_imputada
    ),
    
    perda_total_com_imputacao =
      perda_observada +
      perda_imputada,
    
    percentual_perda_imputada = if_else(
      perda_total_com_imputacao > 0,
      100 * perda_imputada /
        perda_total_com_imputacao,
      0
    )
  )


if (
  anyNA(perdas_imputadas$homicidios_sem_idade) ||
  anyNA(perdas_imputadas$perda_imputada) ||
  anyNA(perdas_imputadas$perda_total_com_imputacao)
) {
  imprimir_completo(
    perdas_imputadas %>%
      filter(
        is.na(homicidios_sem_idade) |
          is.na(perda_imputada) |
          is.na(perda_total_com_imputacao)
      )
  )
  
  stop("Existem valores ausentes nos resultados da imputacao.")
}


if (
  any(perdas_imputadas$perda_imputada < 0) ||
  any(perdas_imputadas$perda_total_com_imputacao < 0)
) {
  stop("Foram encontradas perdas negativas depois da imputacao.")
}


# ----------------------------------------------------------------------
# 6.6. RESULTADO NACIONAL COM IMPUTACAO
# ----------------------------------------------------------------------


dados_brasil_com_imputacao <- perdas_imputadas %>%
  group_by(ano) %>%
  summarise(
    homicidios_com_idade =
      sum(homicidios_com_idade),
    
    homicidios_sem_idade =
      sum(homicidios_sem_idade),
    
    homicidios_totais =
      sum(homicidios_totais),
    
    perda_observada =
      sum(perda_observada),
    
    perda_imputada =
      sum(perda_imputada),
    
    perda_total_com_imputacao =
      sum(perda_total_com_imputacao),
    
    .groups = "drop"
  ) %>%
  mutate(
    percentual_homicidios_imputados = if_else(
      homicidios_totais > 0,
      100 * homicidios_sem_idade /
        homicidios_totais,
      0
    ),
    
    percentual_perda_imputada = if_else(
      perda_total_com_imputacao > 0,
      100 * perda_imputada /
        perda_total_com_imputacao,
      0
    ),
    
    regiao = "Brasil",
    .after = ano
  ) %>%
  arrange(ano)


# ----------------------------------------------------------------------
# 6.7. RESULTADOS REGIONAIS E NACIONAIS NA MESMA TABELA
# ----------------------------------------------------------------------


dados_regiao_com_imputacao <- perdas_imputadas %>%
  select(
    ano,
    regiao,
    homicidios_com_idade,
    homicidios_sem_idade,
    homicidios_totais,
    perda_observada,
    perda_imputada,
    perda_total_com_imputacao,
    percentual_homicidios_imputados,
    percentual_perda_imputada
  )


dados_consolidados_com_imputacao <- bind_rows(
  dados_regiao_com_imputacao,
  dados_brasil_com_imputacao
) %>%
  arrange(
    ano,
    regiao
  )


# ----------------------------------------------------------------------
# 6.8. TESTES DE CONSISTENCIA DA IMPUTACAO
# ----------------------------------------------------------------------


teste_imputacao_anual <- dados_hom_imputacao %>%
  count(
    ano,
    name = "homicidios_identificados_sim"
  ) %>%
  left_join(
    dados_brasil_com_imputacao %>%
      select(
        ano,
        homicidios_com_idade,
        homicidios_sem_idade,
        homicidios_totais
      ),
    by = "ano"
  ) %>%
  mutate(
    diferenca_total =
      homicidios_identificados_sim -
      homicidios_totais,
    
    diferenca_decomposicao =
      homicidios_totais -
      (
        homicidios_com_idade +
          homicidios_sem_idade
      )
  ) %>%
  arrange(ano)


if (
  any(teste_imputacao_anual$diferenca_total != 0) ||
  any(teste_imputacao_anual$diferenca_decomposicao != 0)
) {
  imprimir_completo(
    teste_imputacao_anual %>%
      filter(
        diferenca_total != 0 |
          diferenca_decomposicao != 0
      )
  )
  
  stop(
    paste0(
      "Os totais anuais do SIM nao coincidem com a soma dos ",
      "homicidios observados e imputados."
    )
  )
}


teste_imputacao_regiao_brasil <- perdas_imputadas %>%
  group_by(ano) %>%
  summarise(
    homicidios_com_idade_regioes =
      sum(homicidios_com_idade),
    
    homicidios_sem_idade_regioes =
      sum(homicidios_sem_idade),
    
    homicidios_totais_regioes =
      sum(homicidios_totais),
    
    perda_observada_regioes =
      sum(perda_observada),
    
    perda_imputada_regioes =
      sum(perda_imputada),
    
    perda_total_regioes =
      sum(perda_total_com_imputacao),
    
    .groups = "drop"
  ) %>%
  left_join(
    dados_brasil_com_imputacao %>%
      transmute(
        ano,
        
        homicidios_com_idade_brasil =
          homicidios_com_idade,
        
        homicidios_sem_idade_brasil =
          homicidios_sem_idade,
        
        homicidios_totais_brasil =
          homicidios_totais,
        
        perda_observada_brasil =
          perda_observada,
        
        perda_imputada_brasil =
          perda_imputada,
        
        perda_total_brasil =
          perda_total_com_imputacao
      ),
    by = "ano"
  ) %>%
  mutate(
    diferenca_homicidios_com_idade =
      homicidios_com_idade_regioes -
      homicidios_com_idade_brasil,
    
    diferenca_homicidios_sem_idade =
      homicidios_sem_idade_regioes -
      homicidios_sem_idade_brasil,
    
    diferenca_homicidios_totais =
      homicidios_totais_regioes -
      homicidios_totais_brasil,
    
    diferenca_perda_observada =
      perda_observada_regioes -
      perda_observada_brasil,
    
    diferenca_perda_imputada =
      perda_imputada_regioes -
      perda_imputada_brasil,
    
    diferenca_perda_total =
      perda_total_regioes -
      perda_total_brasil
  )


if (
  any(
    teste_imputacao_regiao_brasil$diferenca_homicidios_com_idade != 0
  ) ||
  any(
    teste_imputacao_regiao_brasil$diferenca_homicidios_sem_idade != 0
  ) ||
  any(
    teste_imputacao_regiao_brasil$diferenca_homicidios_totais != 0
  ) ||
  any(
    abs(
      teste_imputacao_regiao_brasil$diferenca_perda_observada
    ) > 0.01
  ) ||
  any(
    abs(
      teste_imputacao_regiao_brasil$diferenca_perda_imputada
    ) > 0.01
  ) ||
  any(
    abs(
      teste_imputacao_regiao_brasil$diferenca_perda_total
    ) > 0.01
  )
) {
  stop(
    paste0(
      "A soma regional dos resultados imputados difere ",
      "do resultado nacional."
    )
  )
}


# ----------------------------------------------------------------------
# 6.9. CONFERENCIA ESPECIFICA DE 2024
# ----------------------------------------------------------------------


conferencia_imputacao_2024 <- dados_brasil_com_imputacao %>%
  filter(ano == 2024) %>%
  mutate(
    teste_homicidios_com_idade =
      homicidios_com_idade - 42149,
    
    teste_homicidios_sem_idade =
      homicidios_sem_idade - 441,
    
    teste_homicidios_totais =
      homicidios_totais - 42590,
    
    teste_soma =
      homicidios_totais -
      (
        homicidios_com_idade +
          homicidios_sem_idade
      )
  )


if (nrow(conferencia_imputacao_2024) != 1) {
  stop("Nao foi encontrada exatamente uma observacao nacional para 2024.")
}


if (conferencia_imputacao_2024$teste_soma != 0) {
  stop("A decomposicao dos homicidios de 2024 nao fechou.")
}


if (
  conferencia_imputacao_2024$teste_homicidios_com_idade != 0
) {
  warning(
    paste0(
      "O total de homicidios com idade em 2024 nao foi 42.149. ",
      "Valor encontrado: ",
      conferencia_imputacao_2024$homicidios_com_idade,
      "."
    )
  )
}


if (
  conferencia_imputacao_2024$teste_homicidios_sem_idade != 0
) {
  warning(
    paste0(
      "O total de homicidios sem idade em 2024 nao foi 441. ",
      "Valor encontrado: ",
      conferencia_imputacao_2024$homicidios_sem_idade,
      "."
    )
  )
}


if (
  conferencia_imputacao_2024$teste_homicidios_totais != 0
) {
  warning(
    paste0(
      "O total de homicidios em 2024 nao foi 42.590. ",
      "Valor encontrado: ",
      conferencia_imputacao_2024$homicidios_totais,
      "."
    )
  )
}


cat(
  "\nTestes da imputacao concluidos com sucesso.\n",
  "- Todos os homicidios possuem regiao conhecida.\n",
  "- A soma dos casos com e sem idade coincide com o SIM.\n",
  "- A soma das regioes coincide com o resultado nacional.\n",
  "- As perdas observadas e imputadas nao possuem valores ausentes.\n"
)


# ======================================================================
# 7. EXPORTACAO
# ======================================================================


parametros_metodologicos <- tibble(
  parametro = c(
    "Criterio de identificacao dos homicidios",
    "Categorias CID-10 incluidas",
    "Papel de CIRCOBITO",
    "Ano da PNAD Continua",
    "Entrevista da PNAD Continua",
    "Ano inicial dos obitos",
    "Ano final dos obitos",
    "Idade inicial da renda esperada",
    "Idade final do fluxo produtivo",
    "Taxa anual de crescimento real da renda",
    "Taxa anual de desconto",
    "Primeiro fluxo",
    "Tratamento das vitimas menores de 14 anos",
    "Tratamento da renda entre 70 e 90 anos",
    "Tratamento das vitimas com mais de 90 anos",
    "Tratamento dos homicidios sem idade",
    "Nivel da imputacao",
    "Formula da perda imputada"
  ),
  valor = c(
    "Causa basica do obito (CAUSABAS)",
    "X85-X99; Y00-Y09; Y35; Y36",
    "Somente diagnostico; nao define a amostra",
    as.character(ano_pnadc),
    "1",
    as.character(ano_inicio),
    as.character(ano_fim),
    as.character(idade_inicio_renda),
    as.character(idade_final_fluxo),
    as.character(taxa_crescimento_renda),
    as.character(taxa_desconto),
    "Ano seguinte ao homicidio",
    "Fluxo iniciado aos 14 anos",
    "Renda esperada regional da categoria 70+",
    "Valor presente igual a zero",
    paste0(
      "VP medio dos homicidios com idade conhecida ",
      "no mesmo ano e regiao"
    ),
    "Ano x regiao",
    paste0(
      "Homicidios sem idade multiplicados pelo VP medio ",
      "dos homicidios com idade conhecida no mesmo ano e regiao"
    )
  )
)


arquivo_resultados <- file.path(
  pasta_saida,
  "perdas_produtivas_homicidios_resultados_CID10.xlsx"
)


write_xlsx(
  list(
    parametros =
      parametros_metodologicos,
    
    base_pnadc =
      base_pnadc,
    
    diagnostico_renda =
      diagnostico_renda,
    
    comparacao_criterios =
      comparacao_criterios,
    
    diagnostico_obitos =
      diagnostico_homicidios,
    
    diagnostico_unidade_idade =
      diagnostico_unidade_idade,
    
    diagnostico_idades =
      diagnostico_idades,
    
    diagnostico_ano =
      diagnostico_ano,
    
    diagnostico_exclusoes =
      diagnostico_exclusoes,
    
    base_homicidios =
      base_homicidios,
    
    tabua_mortalidade =
      tabua_mortalidade,
    
    trajetoria_renda =
      trajetoria_renda,
    
    grid_vp =
      grid_vp,
    
    diagnostico_grid_vp =
      diagnostico_grid_vp,
    
    diagnostico_variacao_vp =
      diagnostico_variacao_vp,
    
    base_perdas =
      base_perdas,
    
    diagnostico_base_perdas =
      diagnostico_base_perdas,
    
    perdas_ano_regiao =
      perdas_ano_regiao,
    
    perdas_brasil =
      perdas_brasil,
    
    perdas_consolidadas =
      perdas_consolidadas,
    
    teste_agregacao =
      teste_agregacao,
    
    diagnostico_imputacao =
      diagnostico_elegibilidade_imputacao,
    
    homicidios_sem_idade =
      homicidios_sem_idade_ano_regiao,
    
    perdas_imputadas =
      perdas_imputadas,
    
    brasil_com_imputacao =
      dados_brasil_com_imputacao,
    
    consolidado_imputacao =
      dados_consolidados_com_imputacao,
    
    teste_imputacao_anual =
      teste_imputacao_anual,
    
    teste_imputacao_regiao =
      teste_imputacao_regiao_brasil,
    
    conferencia_2024 =
      conferencia_imputacao_2024
  ),
  arquivo_resultados
)


if (!file.exists(arquivo_resultados)) {
  stop(
    paste0(
      "A exportacao terminou, mas o arquivo Excel ",
      "nao foi encontrado."
    )
  )
}


cat(
  "\nCalculo concluido com CAUSABAS como criterio principal.\n",
  
  "Homicidios com idade conhecida:",
  format(
    sum(dados_brasil_com_imputacao$homicidios_com_idade),
    big.mark = ".",
    decimal.mark = ","
  ),
  "\n",
  
  "Homicidios sem idade imputados:",
  format(
    sum(dados_brasil_com_imputacao$homicidios_sem_idade),
    big.mark = ".",
    decimal.mark = ","
  ),
  "\n",
  
  "Total de homicidios:",
  format(
    sum(dados_brasil_com_imputacao$homicidios_totais),
    big.mark = ".",
    decimal.mark = ","
  ),
  "\n",
  
  "Perda produtiva observada:",
  format(
    sum(dados_brasil_com_imputacao$perda_observada),
    big.mark = ".",
    decimal.mark = ",",
    scientific = FALSE,
    digits = 2
  ),
  "\n",
  
  "Perda produtiva imputada:",
  format(
    sum(dados_brasil_com_imputacao$perda_imputada),
    big.mark = ".",
    decimal.mark = ",",
    scientific = FALSE,
    digits = 2
  ),
  "\n",
  
  "Perda produtiva total com imputacao:",
  format(
    sum(
      dados_brasil_com_imputacao$perda_total_com_imputacao
    ),
    big.mark = ".",
    decimal.mark = ",",
    scientific = FALSE,
    digits = 2
  ),
  "\n",
  
  "Arquivo consolidado salvo em:\n",
  arquivo_resultados,
  "\n"
)


cat("\nResultado nacional com imputacao:\n")
imprimir_completo(dados_brasil_com_imputacao)


cat("\nConferencia da imputacao de 2024:\n")
imprimir_completo(conferencia_imputacao_2024)