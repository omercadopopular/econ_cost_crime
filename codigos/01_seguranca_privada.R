# ==============================================================================
# 01 — SEGURANÇA PRIVADA
# Projeto: Custos da Criminalidade no Brasil, 1996-2025
# ==============================================================================
# Escopo deste arquivo
# Reúne as rotinas efetivamente executadas no R para PNAD Anual (1996-2001, 2002-2009 e 2011) e PNAD Contínua (2012-2025). Os preenchimentos de 2000 e 2010, a deflação e a consolidação formal/informal permanecem na planilha final.
#
# Reprodutibilidade
# 1. Ajuste somente os caminhos em "CONFIGURACAO".
# 2. Instale previamente os pacotes listados; o script não instala pacotes.
# 3. As etapas feitas em Excel são identificadas e não são recriadas aqui.
# 4. As saídas são gravadas em dir_saida sem chamadas interativas.
# ==============================================================================


options(stringsAsFactors = FALSE, survey.lonely.psu = "adjust")


# CONFIGURACAO ---------------------------------------------------------------
# Ajuste apenas `dir_projeto` caso a pasta principal seja movida.
# O script testa automaticamente as duas estruturas de pasta mais prováveis
# para os microdados antigos: `pnad/_antiga` e `pnad_antiga`.
dir_projeto <- "C:/Users/Lucas Simões/Desktop/CEC Brasil"

candidatos_pnad_antiga <- c(
  file.path(dir_projeto, "pnad", "_antiga"),
  file.path(dir_projeto, "pnad_antiga")
)

candidatos_existentes <- candidatos_pnad_antiga[dir.exists(candidatos_pnad_antiga)]

if (length(candidatos_existentes) == 0L) {
  stop(
    "Não foi localizada a pasta principal da PNAD antiga. Caminhos testados: ",
    paste(candidatos_pnad_antiga, collapse = " | "),
    call. = FALSE
  )
}

if (length(candidatos_existentes) > 1L) {
  warning(
    "Mais de uma pasta candidata da PNAD antiga foi encontrada. Será usada: ",
    candidatos_existentes[1L],
    call. = FALSE
  )
}

dir_pnad_antiga <- normalizePath(
  candidatos_existentes[1L],
  winslash = "/",
  mustWork = TRUE
)

dir_saida <- file.path(dir_projeto, "resultados", "seguranca_privada")
dir.create(dir_saida, recursive = TRUE, showWarnings = FALSE)

message("PNAD antiga: ", dir_pnad_antiga)
message("Saídas: ", normalizePath(dir_saida, winslash = "/", mustWork = TRUE))


pacotes <- c("data.table","readr","dplyr","tidyr","stringr","purrr","survey",
             "PNADcIBGE","writexl")
faltantes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]
if (length(faltantes)) stop("Instale os pacotes: ", paste(faltantes, collapse = ", "))


# PNAD ANUAL 1996-2001 -------------------------------------------------------
local({
# ============================================================================
# PNAD ANUAL 1996-2001 — TRABALHADORES E RENDIMENTOS EM SEGURANCA PRIVADA
# ============================================================================
#
# OBJETIVO
# --------
# Estimar, para 1996, 1997, 1998, 1999 e 2001, o número de trabalhadores,
# o rendimento médio mensal e a massa de rendimentos em ocupações relacionadas
# à segurança privada. Não houve PNAD em 2000 por causa da realização do Censo.
#
# RECORTES OCUPACIONAIS
# ---------------------
#   1. Estrito: códigos 843 e 869.
#   2. Amplo:   códigos 841, 843 e 869.
#
# POPULAÇÃO ANALISADA
# -------------------
# Pessoas ocupadas no trabalho principal (condição = 1) e nas posições:
#   01 = empregado com carteira;
#   04 = empregado sem carteira;
#   09 = conta própria;
#   10 = empregador.
#
# As posições 03, 06, 07 e 13 — militares/estatutários e outras categorias
# fora do recorte adotado — não entram nas estimativas.
#
# RENDIMENTO E IMPUTAÇÃO
# ----------------------
# Utiliza-se o rendimento mensal do trabalho principal. Valores vazios,
# não numéricos, negativos e o código 999999999999 (ignorado) são tratados
# como ausentes. Para cada ano, rendimentos ausentes são imputados pela média
# ponderada dos declarantes da mesma célula ocupação x posição. O programa
# interrompe a execução se uma célula que precisa de imputação não tiver doador.
#
# ESTIMATIVAS
# -----------
# Todas as estatísticas utilizam o peso da pessoa. A massa anual corresponde a
# 12 vezes a massa mensal. Os valores são nominais do próprio ano, sem encargos
# patronais e sem deflação.
#
# INSUMOS ESPERADOS
# -----------------
# Pasta principal:
#   <dir_pnad_antiga>/<ano>
#
# Arquivos de pessoas:
#   1996/P96BR.TXT
#   1997/Pessoas97.txt
#   1998/Pessoa98.txt
#   1999/Pessoa99.txt
#   2001/Dados/PES2001.TXT
#
# SAÍDAS
# ------
# Os CSVs são gravados, com separador ";" e decimal ",", na pasta
# resultados/seguranca_privada/pnad_1996_2001.
# ============================================================================




# 0. PACOTE ------------------------------------------------------------------


if (!requireNamespace("data.table", quietly = TRUE)) {
  stop(
    "O pacote 'data.table' não está instalado. ",
    "Instale-o uma única vez com install.packages('data.table')."
  )
}


library(data.table)




# 1. CONFIGURAÇÕES -----------------------------------------------------------


pasta_pnad <- dir_pnad_antiga


pasta_resultados <- file.path(dir_saida, "pnad_1996_2001")


anos_analisados <- c(1996L, 1997L, 1998L, 1999L, 2001L)


codigos_estrito <- c("843", "869")
codigos_amplo <- c("841", "843", "869")
posicoes_incluidas <- c("01", "04", "09", "10")
codigo_renda_ignorada <- 999999999999


if (!dir.exists(pasta_pnad)) {
  stop("A pasta principal da PNAD não foi localizada: ", pasta_pnad)
}


if (!dir.exists(pasta_resultados)) {
  dir.create(pasta_resultados, recursive = TRUE)
}




# 2. ARQUIVOS E LEIAUTES -----------------------------------------------------


# As posições abaixo foram verificadas nos dicionários e validadas em uma
# leitura diagnóstica de 200 mil registros por ano.


configuracao_anos <- data.table(
  ano = anos_analisados,
  caminho_relativo = c(
    file.path("1996", "P96BR.TXT"),
    file.path("1997", "Pessoas97.txt"),
    file.path("1998", "Pessoa98.txt"),
    file.path("1999", "Pessoa99.txt"),
    file.path("2001", "Dados", "PES2001.TXT")
  ),
  ocupacao_inicio = c(158L, 158L, 125L, 125L, 83L),
  ocupacao_tamanho = rep(3L, 5L),
  condicao_inicio = c(1414L, 1149L, 644L, 644L, 623L),
  condicao_tamanho = rep(1L, 5L),
  posicao_inicio = c(1415L, 1150L, 645L, 645L, 624L),
  posicao_tamanho = rep(2L, 5L),
  renda_inicio = c(1431L, 1166L, 661L, 661L, 640L),
  renda_tamanho = rep(12L, 5L),
  peso_inicio = c(1511L, 1246L, 741L, 741L, 720L),
  peso_tamanho = rep(5L, 5L)
)




# 3. FUNÇÕES AUXILIARES ------------------------------------------------------


extrair_campo <- function(linhas, inicio, tamanho) {
  trimws(substr(linhas, inicio, inicio + tamanho - 1L))
}


converter_numero <- function(x) {
  x <- trimws(x)
  resultado <- rep(NA_real_, length(x))
  valido <- !is.na(x) & grepl("^-?[0-9]+$", x)
  resultado[valido] <- suppressWarnings(as.numeric(x[valido]))
  resultado
}


media_ponderada <- function(x, peso) {
  valido <- !is.na(x) & !is.na(peso) & peso > 0
  if (!any(valido)) return(NA_real_)
  weighted.mean(x[valido], peso[valido])
}


soma_ponderada <- function(x, peso) {
  valido <- !is.na(x) & !is.na(peso) & peso > 0
  if (!any(valido)) return(NA_real_)
  sum(x[valido] * peso[valido])
}


formatar_inteiro <- function(x) {
  format(
    x,
    big.mark = ".",
    decimal.mark = ",",
    scientific = FALSE,
    trim = TRUE
  )
}


validar_configuracao <- function(configuracao) {
  if (nrow(configuracao) != length(anos_analisados)) {
    stop("A tabela de configuração não contém exatamente um registro por ano.")
  }
  
  if (anyDuplicated(configuracao$ano)) {
    stop("Há anos duplicados na tabela de configuração.")
  }
  
  campos_posicao <- grep(
    "_(inicio|tamanho)$",
    names(configuracao),
    value = TRUE
  )
  
  if (length(campos_posicao) == 0L) {
    stop("Nenhuma coluna de posição ou tamanho foi encontrada na configuração.")
  }
  
  colunas_nao_numericas <- campos_posicao[
    !vapply(
      configuracao[, ..campos_posicao],
      is.numeric,
      logical(1L)
    )
  ]
  
  if (length(colunas_nao_numericas) > 0L) {
    stop(
      "As seguintes colunas deveriam ser numéricas: ",
      paste(colunas_nao_numericas, collapse = ", ")
    )
  }
  
  valores_configuracao <- unlist(
    configuracao[, ..campos_posicao],
    use.names = FALSE
  )
  
  if (anyNA(valores_configuracao)) {
    stop("Há valores ausentes nas posições ou tamanhos dos campos.")
  }
  
  if (any(valores_configuracao <= 0)) {
    stop("Há posição ou tamanho de campo menor ou igual a zero na configuração.")
  }
  
  invisible(TRUE)
}


validar_configuracao(configuracao_anos)




# 4. OBJETOS DE RESULTADO ----------------------------------------------------


lista_estimativas_detalhadas <- vector("list", length(anos_analisados))
lista_imputacao <- vector("list", length(anos_analisados))
lista_qualidade <- vector("list", length(anos_analisados))
lista_arquivos <- vector("list", length(anos_analisados))




# 5. LEITURA, LIMPEZA E IMPUTAÇÃO -------------------------------------------


for (i in seq_along(anos_analisados)) {
  ano_atual <- anos_analisados[i]
  cfg <- configuracao_anos[ano == ano_atual]
  arquivo_pessoas <- file.path(pasta_pnad, cfg$caminho_relativo)

  # Primeiro tenta o caminho historicamente usado. Se a organização interna da
  # pasta do ano for diferente, procura recursivamente pelo mesmo nome de arquivo.
  if (!file.exists(arquivo_pessoas)) {
    pasta_ano <- file.path(pasta_pnad, as.character(ano_atual))

    if (!dir.exists(pasta_ano)) {
      stop(
        "A pasta da PNAD de ", ano_atual,
        " não foi localizada: ", pasta_ano,
        call. = FALSE
      )
    }

    nome_esperado <- basename(cfg$caminho_relativo)
    arquivos_ano <- list.files(
      pasta_ano,
      recursive = TRUE,
      full.names = TRUE,
      all.files = FALSE
    )

    candidatos <- arquivos_ano[
      tolower(basename(arquivos_ano)) == tolower(nome_esperado)
    ]

    if (length(candidatos) == 1L) {
      arquivo_pessoas <- candidatos[1L]
    } else if (length(candidatos) == 0L) {
      stop(
        "O arquivo de pessoas de ", ano_atual,
        " não foi localizado. Nome procurado: ", nome_esperado,
        ". Pasta pesquisada: ", pasta_ano,
        call. = FALSE
      )
    } else {
      stop(
        "Foram encontrados ", length(candidatos),
        " arquivos chamados ", nome_esperado,
        " para ", ano_atual,
        ". Mantenha apenas um candidato ou ajuste `configuracao_anos`.",
        call. = FALSE
      )
    }
  }
  
  cat(
    "\n==================================================\n",
    "PNAD ", ano_atual, "\n",
    "Arquivo: ", normalizePath(arquivo_pessoas, winslash = "/"), "\n",
    "==================================================\n",
    sep = ""
  )
  
  # Lê o arquivo completo. A opção skipNul protege contra bytes nulos
  # ocasionais sem alterar a posição dos demais campos do registro.
  linhas <- readLines(
    arquivo_pessoas,
    warn = FALSE,
    encoding = "latin1",
    skipNul = TRUE
  )
  
  if (length(linhas) == 0L) {
    stop("O arquivo de ", ano_atual, " não contém registros legíveis.")
  }
  
  dados <- data.table(
    ocupacao = extrair_campo(
      linhas, cfg$ocupacao_inicio, cfg$ocupacao_tamanho
    ),
    condicao = extrair_campo(
      linhas, cfg$condicao_inicio, cfg$condicao_tamanho
    ),
    posicao = extrair_campo(
      linhas, cfg$posicao_inicio, cfg$posicao_tamanho
    ),
    renda_original = converter_numero(
      extrair_campo(linhas, cfg$renda_inicio, cfg$renda_tamanho)
    ),
    peso = converter_numero(
      extrair_campo(linhas, cfg$peso_inicio, cfg$peso_tamanho)
    )
  )
  
  registros_lidos <- nrow(dados)
  
  # O peso é indispensável para todas as estimativas.
  pesos_invalidos <- dados[, sum(is.na(peso) | peso <= 0)]
  if (pesos_invalidos > 0L) {
    stop(
      "Foram encontrados ", pesos_invalidos,
      " pesos ausentes ou não positivos em ", ano_atual, "."
    )
  }
  
  # Conserva somente a população-alvo comum aos dois cenários.
  dados <- dados[
    ocupacao %chin% codigos_amplo &
      condicao == "1" &
      posicao %chin% posicoes_incluidas
  ]
  
  if (nrow(dados) == 0L) {
    stop("Nenhum trabalhador do recorte amplo foi encontrado em ", ano_atual, ".")
  }
  
  dados[
    is.na(renda_original) |
      renda_original < 0 |
      renda_original == codigo_renda_ignorada,
    renda_original := NA_real_
  ]
  
  dados[, renda_ausente := is.na(renda_original)]
  
  # Média dos doadores na célula ocupação x posição, usando o peso da pessoa.
  doadores <- dados[
    renda_ausente == FALSE,
    .(
      observacoes_doadoras = .N,
      trabalhadores_doadores = sum(peso),
      media_ponderada_doadores = media_ponderada(renda_original, peso)
    ),
    by = .(ocupacao, posicao)
  ]
  
  necessitam_imputacao <- dados[
    renda_ausente == TRUE,
    .(observacoes_receptoras = .N),
    by = .(ocupacao, posicao)
  ]
  
  sem_doador <- necessitam_imputacao[
    !doadores,
    on = .(ocupacao, posicao)
  ]
  
  if (nrow(sem_doador) > 0L) {
    stop(
      "Há célula(s) com renda ausente e sem doador em ", ano_atual,
      ": ",
      paste(
        paste0(sem_doador$ocupacao, " x ", sem_doador$posicao),
        collapse = ", "
      )
    )
  }
  
  dados[
    doadores,
    on = .(ocupacao, posicao),
    renda_imputada := i.media_ponderada_doadores
  ]
  
  dados[
    ,
    renda_final := fifelse(
      renda_ausente,
      renda_imputada,
      renda_original
    )
  ]
  
  if (anyNA(dados$renda_final)) {
    stop("A imputação deixou rendimentos ausentes em ", ano_atual, ".")
  }
  
  # Tabela de auditoria da imputação, inclusive para células sem receptores.
  auditoria <- merge(
    dados[
      ,
      .(
        observacoes = .N,
        observacoes_com_renda = sum(!renda_ausente),
        observacoes_imputadas = sum(renda_ausente),
        trabalhadores = sum(peso),
        trabalhadores_com_renda = sum(peso[!renda_ausente]),
        trabalhadores_imputados = sum(peso[renda_ausente])
      ),
      by = .(ocupacao, posicao)
    ],
    doadores,
    by = c("ocupacao", "posicao"),
    all.x = TRUE
  )
  
  auditoria[, ano := ano_atual]
  setcolorder(auditoria, c("ano", setdiff(names(auditoria), "ano")))
  lista_imputacao[[i]] <- auditoria
  
  # Classificação operacional usada também nas análises de 2002-2009 e 2011.
  dados[
    ,
    grupo_posicao := fifelse(
      posicao == "01",
      "formal",
      "demais_posicoes"
    )
  ]
  
  # Duplica os registros conforme o cenário ao qual pertencem. Os códigos 843
  # e 869 entram nos dois cenários; o código 841 entra somente no amplo.
  dados_cenarios <- rbindlist(
    list(
      dados[ocupacao %chin% codigos_estrito][, cenario := "estrito"],
      copy(dados)[, cenario := "amplo"]
    ),
    use.names = TRUE
  )
  
  # Estimativas por cenário, grupo de posição e código ocupacional.
  detalhadas <- dados_cenarios[
    ,
    .(
      observacoes_amostrais = .N,
      observacoes_imputadas = sum(renda_ausente),
      trabalhadores = sum(peso),
      trabalhadores_com_renda_imputada = sum(peso[renda_ausente]),
      rendimento_medio_mensal = media_ponderada(renda_final, peso),
      massa_mensal = soma_ponderada(renda_final, peso)
    ),
    by = .(cenario, grupo_posicao, ocupacao)
  ]
  
  detalhadas[, `:=`(
    ano = ano_atual,
    massa_anual = 12 * massa_mensal
  )]
  
  setcolorder(
    detalhadas,
    c(
      "ano", "cenario", "grupo_posicao", "ocupacao",
      "observacoes_amostrais", "observacoes_imputadas",
      "trabalhadores", "trabalhadores_com_renda_imputada",
      "rendimento_medio_mensal", "massa_mensal", "massa_anual"
    )
  )
  
  lista_estimativas_detalhadas[[i]] <- detalhadas
  
  lista_qualidade[[i]] <- data.table(
    ano = ano_atual,
    registros_lidos = registros_lidos,
    registros_populacao_alvo = nrow(dados),
    registros_renda_declarada = sum(!dados$renda_ausente),
    registros_renda_imputada = sum(dados$renda_ausente),
    proporcao_registros_imputados = mean(dados$renda_ausente),
    trabalhadores_populacao_alvo = sum(dados$peso),
    trabalhadores_renda_imputada = sum(dados$peso[dados$renda_ausente]),
    proporcao_ponderada_imputada =
      sum(dados$peso[dados$renda_ausente]) / sum(dados$peso)
  )
  
  lista_arquivos[[i]] <- data.table(
    ano = ano_atual,
    arquivo = normalizePath(arquivo_pessoas, winslash = "/"),
    tamanho_bytes = file.info(arquivo_pessoas)$size
  )
  
  cat(
    "Registros lidos: ", formatar_inteiro(registros_lidos), "\n",
    "Registros no recorte amplo: ", formatar_inteiro(nrow(dados)), "\n",
    "Registros com renda imputada: ",
    formatar_inteiro(sum(dados$renda_ausente)), "\n",
    sep = ""
  )
  
  rm(
    linhas, dados, dados_cenarios, doadores, necessitam_imputacao,
    sem_doador, auditoria, detalhadas
  )
  gc()
}




# 6. CONSOLIDAÇÃO ------------------------------------------------------------


estimativas_detalhadas <- rbindlist(
  lista_estimativas_detalhadas,
  use.names = TRUE,
  fill = TRUE
)


auditoria_imputacao <- rbindlist(lista_imputacao, use.names = TRUE, fill = TRUE)
controle_qualidade <- rbindlist(lista_qualidade, use.names = TRUE, fill = TRUE)
arquivos_utilizados <- rbindlist(lista_arquivos, use.names = TRUE, fill = TRUE)


# Agrega a tabela detalhada em cenário x grupo de posição.
resultados_grupo <- estimativas_detalhadas[
  ,
  .(
    observacoes_amostrais = sum(observacoes_amostrais),
    observacoes_imputadas = sum(observacoes_imputadas),
    trabalhadores = sum(trabalhadores),
    trabalhadores_com_renda_imputada =
      sum(trabalhadores_com_renda_imputada),
    massa_mensal = sum(massa_mensal),
    massa_anual = sum(massa_anual)
  ),
  by = .(ano, cenario, grupo_posicao)
]


resultados_grupo[
  ,
  rendimento_medio_mensal := massa_mensal / trabalhadores
]


# Agrega formal + demais posições para produzir a série principal por cenário.
serie_principal <- resultados_grupo[
  ,
  .(
    observacoes_amostrais = sum(observacoes_amostrais),
    observacoes_imputadas = sum(observacoes_imputadas),
    trabalhadores = sum(trabalhadores),
    trabalhadores_com_renda_imputada =
      sum(trabalhadores_com_renda_imputada),
    massa_mensal = sum(massa_mensal),
    massa_anual = sum(massa_anual)
  ),
  by = .(ano, cenario)
]


serie_principal[
  ,
  `:=`(
    rendimento_medio_mensal = massa_mensal / trabalhadores,
    proporcao_trabalhadores_imputados =
      trabalhadores_com_renda_imputada / trabalhadores
  )
]


setcolorder(
  serie_principal,
  c(
    "ano", "cenario", "observacoes_amostrais", "observacoes_imputadas",
    "trabalhadores", "trabalhadores_com_renda_imputada",
    "proporcao_trabalhadores_imputados", "rendimento_medio_mensal",
    "massa_mensal", "massa_anual"
  )
)


setorder(serie_principal, ano, cenario)
setorder(resultados_grupo, ano, cenario, grupo_posicao)
setorder(estimativas_detalhadas, ano, cenario, grupo_posicao, ocupacao)
setorder(auditoria_imputacao, ano, ocupacao, posicao)
setorder(controle_qualidade, ano)
setorder(arquivos_utilizados, ano)




# 7. TESTES DE CONSISTÊNCIA --------------------------------------------------


if (serie_principal[, uniqueN(cenario), by = ano][, any(V1 != 2L)]) {
  stop("Nem todos os anos possuem os dois cenários esperados.")
}


comparacao_cenarios <- dcast(
  serie_principal,
  ano ~ cenario,
  value.var = c("trabalhadores", "massa_anual")
)


if (comparacao_cenarios[, any(trabalhadores_amplo < trabalhadores_estrito)]) {
  stop("Em pelo menos um ano, o cenário amplo tem menos trabalhadores.")
}


if (comparacao_cenarios[, any(massa_anual_amplo < massa_anual_estrito)]) {
  stop("Em pelo menos um ano, o cenário amplo tem massa anual menor.")
}


if (any(!is.finite(serie_principal$rendimento_medio_mensal)) ||
    any(serie_principal$rendimento_medio_mensal < 0)) {
  stop("A série principal contém rendimento médio inválido.")
}




# 8. EXPORTAÇÃO --------------------------------------------------------------


fwrite(
  serie_principal,
  file.path(pasta_resultados, "01_serie_principal_1996_2001.csv"),
  sep = ";", dec = ",", bom = TRUE
)


fwrite(
  resultados_grupo,
  file.path(pasta_resultados, "02_resultados_por_grupo_posicao.csv"),
  sep = ";", dec = ",", bom = TRUE
)


fwrite(
  estimativas_detalhadas,
  file.path(pasta_resultados, "03_resultados_por_ocupacao_posicao.csv"),
  sep = ";", dec = ",", bom = TRUE
)


fwrite(
  auditoria_imputacao,
  file.path(pasta_resultados, "04_auditoria_imputacao.csv"),
  sep = ";", dec = ",", bom = TRUE
)


fwrite(
  controle_qualidade,
  file.path(pasta_resultados, "05_controle_qualidade.csv"),
  sep = ";", dec = ",", bom = TRUE
)


fwrite(
  arquivos_utilizados,
  file.path(pasta_resultados, "06_arquivos_utilizados.csv"),
  sep = ";", dec = ",", bom = TRUE
)




# 9. RESULTADO NO CONSOLE ----------------------------------------------------


cat(
  "\n==================================================\n",
  "PROCESSAMENTO CONCLUÍDO\n",
  "==================================================\n",
  "Resultados gravados em:\n",
  normalizePath(pasta_resultados, winslash = "/"),
  "\n\nSérie principal:\n",
  sep = ""
)


print(serie_principal)


cat(
  "\nObservação: 2000 não aparece na série porque não houve PNAD naquele ano.\n",
  "Os valores são nominais, sem encargos patronais e sem deflação.\n",
  sep = ""
)


})


# PNAD ANUAL 2002-2009 -------------------------------------------------------
local({
# ============================================================================
# PNAD ANUAL 2002-2009 — TRABALHADORES E RENDIMENTOS EM SEGURANCA PRIVADA
# ============================================================================
# Objetivo
#   Reproduzir, para 2002-2009, os dois recortes ocupacionais usados na PNAD
#   2011 e gerar uma serie auditavel de trabalhadores e massa de rendimentos.
#
# Fonte
#   Pacotes reponderados da PNAD anual/IBGE. Para cada ano, o programa usa:
#     - PESAAAA.txt: microdados de pessoas em largura fixa;
#     - INPUT PESAAAA.txt: programa SAS oficial com posicoes e larguras.
#
# Conceito medido
#   Massa do rendimento mensal do trabalho principal, ponderada pelo peso da
#   pessoa e anualizada por 12. Os valores sao nominais do respectivo ano,
#   sem encargos patronais e sem deflacao. Portanto, nao representam ainda o
#   custo total do empregador nem pagamentos retrospectivamente observados.
#
# Cenarios
#   - estrito: CBO-domiciliar 5173;
#   - amplo:   CBO-domiciliar 5173 ou 5174.
#
# Posicoes mantidas (V4706)
#   01 = empregado com carteira;
#   04 = outro empregado sem carteira;
#   09 = conta propria;
#   10 = empregador.
#   Militares e estatutarios nao entram, evitando sobreposicao direta com o
#   eixo de seguranca publica. A classificacao formal/informal usada nas
#   saidas e apenas operacional: 01 = formal; 04/09/10 = demais_posicoes.
#
# Rendimento ausente
#   V4718 igual a 999999999999, vazio ou nao numerico e tratado como ausente.
#   A imputacao principal e a media ponderada dos declarantes da mesma celula
#   ocupacao x posicao, separadamente em cada ano. O script para caso nao haja
#   nenhum doador em uma celula que precise de imputacao.
#
# Requisitos
#   R >= 4.1; pacotes readr e data.table instalados.
# ============================================================================


# 1. CONFIGURACAO -------------------------------------------------------------


pasta_pnad <- dir_pnad_antiga
anos <- 2002:2009


ocupacoes_amplas <- c("5173", "5174")
ocupacoes_estritas <- "5173"
posicoes_incluidas <- c("01", "04", "09", "10")
codigo_renda_ignorada <- "999999999999"


pasta_saida <- file.path(dir_saida, "pnad_2002_2009")
dir.create(pasta_saida, recursive = TRUE, showWarnings = FALSE)


pacotes <- c("readr", "data.table")
faltantes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]
if (length(faltantes)) {
  stop("Instale antes os pacotes: ", paste(faltantes, collapse = ", "),
       ". Exemplo: install.packages(c(",
       paste(sprintf("\"%s\"", faltantes), collapse = ", "), "))")
}


# 2. FUNCOES DE INFRAESTRUTURA ------------------------------------------------


localizar_arquivo <- function(ano, tipo = c("dados", "input")) {
  tipo <- match.arg(tipo)
  pasta_ano <- file.path(pasta_pnad, as.character(ano))
  if (!dir.exists(pasta_ano)) stop("Pasta inexistente: ", pasta_ano)


  arqs <- list.files(pasta_ano, recursive = TRUE, full.names = TRUE,
                     ignore.case = TRUE)
  eh_pes <- grepl(paste0("PES", ano, "\\.txt$"), basename(arqs),
                  ignore.case = TRUE)
  eh_input <- grepl("input", basename(arqs), ignore.case = TRUE)
  candidatos <- if (tipo == "dados") arqs[eh_pes & !eh_input] else arqs[eh_pes & eh_input]


  if (length(candidatos) != 1L) {
    stop("Ano ", ano, ": encontrados ", length(candidatos),
         " arquivos do tipo ", tipo, "; era esperado exatamente 1.")
  }
  candidatos
}


# Extrai do programa SAS linhas como: @00668 V4704 $1.
# O regex aceita espacos, tabulacoes, variaveis numericas/caractere e casos em
# que o comentario comeca imediatamente apos o ponto (como V4718 em 2008/09).
ler_layout_sas <- function(arquivo_input) {
  linhas <- readLines(arquivo_input, warn = FALSE, encoding = "latin1")
  rx <- "@([0-9]+)[[:space:]]+([A-Za-z][A-Za-z0-9_]*)[[:space:]]+(\\$?)([0-9]+)\\."
  m <- regexec(rx, linhas, perl = TRUE)
  partes <- regmatches(linhas, m)
  partes <- partes[lengths(partes) == 5L]
  if (!length(partes)) stop("Nenhum campo SAS reconhecido em: ", arquivo_input)


  tab <- data.table::rbindlist(lapply(partes, function(x) {
    data.table::data.table(
      inicio = as.integer(x[2]), variavel = toupper(x[3]),
      caractere = identical(x[4], "$"), largura = as.integer(x[5])
    )
  }))
  tab[, fim := inicio + largura - 1L]
  tab[]
}


normalizar_codigo <- function(x, largura) {
  x <- trimws(as.character(x))
  x[x == ""] <- NA_character_
  ok <- !is.na(x) & grepl("^[0-9]+$", x)
  x[ok] <- sprintf(paste0("%0", largura, "d"), as.integer(x[ok]))
  x
}


media_ponderada_segura <- function(x, w) {
  ok <- is.finite(x) & is.finite(w) & w > 0
  if (!any(ok)) return(NA_real_)
  sum(x[ok] * w[ok]) / sum(w[ok])
}


assert_quase_igual <- function(a, b, rotulo, tol = 1e-7) {
  escala <- max(1, abs(a), abs(b))
  if (!isTRUE(all.equal(a, b, tolerance = tol * escala))) {
    stop("Falha de consistencia em ", rotulo, ": ", a, " versus ", b)
  }
}


# 3. LEITURA E TRATAMENTO DE UM ANO ------------------------------------------


processar_ano <- function(ano) {
  message("\n--- Processando PNAD ", ano, " ---")
  arq_dados <- localizar_arquivo(ano, "dados")
  arq_input <- localizar_arquivo(ano, "input")
  layout <- ler_layout_sas(arq_input)


  vars <- c("V4704", "V4706", "V4718", "V4729", "V9906", "V9907")
  ausentes <- setdiff(vars, layout$variavel)
  if (length(ausentes)) stop("Ano ", ano, ": variaveis ausentes no leiaute: ",
                             paste(ausentes, collapse = ", "))
  lay <- layout[match(vars, variavel)]
  if (anyDuplicated(lay$variavel)) stop("Ano ", ano, ": variavel duplicada no leiaute.")


  # Todos os campos entram inicialmente como texto, preservando zeros a esquerda
  # e permitindo o tratamento explicito dos codigos especiais.
  pos <- readr::fwf_positions(start = lay$inicio, end = lay$fim,
                             col_names = lay$variavel)
  tipos <- do.call(readr::cols, c(
    setNames(rep(list(readr::col_character()), nrow(lay)), lay$variavel),
    list(.default = readr::col_skip())
  ))
  d <- data.table::as.data.table(readr::read_fwf(
    arq_dados, col_positions = pos, col_types = tipos,
    trim_ws = FALSE, progress = interactive(),
    locale = readr::locale(encoding = "Latin1")
  ))


  # Padronizacao dos codigos usados nos filtros.
  d[, V4704 := normalizar_codigo(V4704, 1L)]
  d[, V4706 := normalizar_codigo(V4706, 2L)]
  d[, V9906 := normalizar_codigo(V9906, 4L)]
  d[, V9907 := trimws(V9907)]
  d[, peso := suppressWarnings(as.numeric(trimws(V4729)))]
  d[, renda_texto := trimws(V4718)]
  d[renda_texto %in% c("", codigo_renda_ignorada), renda_texto := NA_character_]
  d[, renda_observada := suppressWarnings(as.numeric(renda_texto))]


  if (any(!is.finite(d$peso) | d$peso <= 0, na.rm = TRUE)) {
    stop("Ano ", ano, ": ha pesos nao positivos ou infinitos.")
  }


  # V4704=1: economicamente ativa na semana; os filtros de ocupacao e posicao
  # tornam a condicao redundante na maioria dos registros, mas ela e mantida
  # como trava conceitual explicita.
  base <- d[V4704 == "1" & V9906 %in% ocupacoes_amplas &
              V4706 %in% posicoes_incluidas & is.finite(peso) & peso > 0]
  if (!nrow(base)) stop("Ano ", ano, ": o filtro produziu zero observacoes.")


  # Diagnostica rendas negativas ou codigos especiais nao previstos.
  if (any(base$renda_observada < 0, na.rm = TRUE)) {
    stop("Ano ", ano, ": renda negativa encontrada apos a limpeza.")
  }


  # Media ponderada de doadores dentro de ocupacao x posicao.
  doadores <- base[is.finite(renda_observada), .(
    n_doadores = .N,
    peso_doadores = sum(peso),
    media_imputacao = media_ponderada_segura(renda_observada, peso)
  ), by = .(V9906, V4706)]
  base <- merge(base, doadores, by = c("V9906", "V4706"), all.x = TRUE,
                sort = FALSE)
  base[, imputada := !is.finite(renda_observada)]
  if (base[imputada == TRUE, any(!is.finite(media_imputacao))]) {
    cel <- unique(base[imputada == TRUE & !is.finite(media_imputacao),
                       paste(V9906, V4706, sep = " x ")])
    stop("Ano ", ano, ": celula(s) sem doador para imputacao: ",
         paste(cel, collapse = ", "))
  }
  base[, renda_final := data.table::fifelse(imputada, media_imputacao, renda_observada)]
  base[, formalidade := data.table::fifelse(
    V4706 == "01", "formal_carteira", "demais_posicoes"
  )]
  base[, ano := ano]


  calcular_cenario <- function(nome, ocupacoes) {
    z <- base[V9906 %in% ocupacoes]
    if (!nrow(z)) stop("Ano ", ano, ", cenario ", nome, ": zero observacoes.")


    total <- z[, .(
      observacoes = .N,
      pessoas = sum(peso),
      renda_media_mensal = media_ponderada_segura(renda_final, peso),
      massa_mensal = sum(peso * renda_final),
      massa_anual = 12 * sum(peso * renda_final),
      observacoes_imputadas = sum(imputada),
      taxa_imputacao_amostral = mean(imputada),
      pessoas_imputadas = sum(peso[imputada]),
      taxa_imputacao_ponderada = sum(peso[imputada]) / sum(peso),
      massa_anual_imputada = 12 * sum(peso[imputada] * renda_final[imputada]),
      participacao_massa_imputada = sum(peso[imputada] * renda_final[imputada]) /
        sum(peso * renda_final)
    )]
    total[, `:=`(ano = ano, cenario = nome)]


    detalhe <- z[, .(
      observacoes = .N, pessoas = sum(peso),
      renda_media_mensal = media_ponderada_segura(renda_final, peso),
      massa_mensal = sum(peso * renda_final),
      massa_anual = 12 * sum(peso * renda_final),
      observacoes_imputadas = sum(imputada),
      pessoas_imputadas = sum(peso[imputada])
    ), by = .(ocupacao = V9906, posicao = V4706, formalidade)]
    detalhe[, `:=`(ano = ano, cenario = nome)]


    por_formalidade <- z[, .(
      observacoes = .N, pessoas = sum(peso),
      renda_media_mensal = media_ponderada_segura(renda_final, peso),
      massa_mensal = sum(peso * renda_final),
      massa_anual = 12 * sum(peso * renda_final)
    ), by = formalidade]
    por_formalidade[, `:=`(ano = ano, cenario = nome)]


    # Identidades contabeis fundamentais.
    assert_quase_igual(total$pessoas, sum(detalhe$pessoas),
                       paste(ano, nome, "pessoas/detalhe"))
    assert_quase_igual(total$massa_anual, sum(detalhe$massa_anual),
                       paste(ano, nome, "massa/detalhe"))
    assert_quase_igual(total$pessoas, sum(por_formalidade$pessoas),
                       paste(ano, nome, "pessoas/formalidade"))
    assert_quase_igual(total$massa_anual, 12 * total$massa_mensal,
                       paste(ano, nome, "anualizacao"))


    list(total = total, detalhe = detalhe, formalidade = por_formalidade)
  }


  amplo <- calcular_cenario("amplo_5173_5174", ocupacoes_amplas)
  estrito <- calcular_cenario("estrito_5173", ocupacoes_estritas)


  # Auditoria compacta: sem microdados pessoais/identificadores.
  diagnostico_celulas <- base[, .(
    observacoes = .N, pessoas = sum(peso),
    observacoes_imputadas = sum(imputada),
    pessoas_imputadas = sum(peso[imputada]),
    taxa_imputacao_amostral = mean(imputada),
    taxa_imputacao_ponderada = sum(peso[imputada]) / sum(peso),
    media_imputacao = unique(media_imputacao)[1L]
  ), by = .(ano, ocupacao = V9906, posicao = V4706)]


  list(
    totais = data.table::rbindlist(list(amplo$total, estrito$total), fill = TRUE),
    detalhe = data.table::rbindlist(list(amplo$detalhe, estrito$detalhe), fill = TRUE),
    formalidade = data.table::rbindlist(list(amplo$formalidade, estrito$formalidade), fill = TRUE),
    diagnostico = diagnostico_celulas,
    layout = lay[, .(ano = ano, variavel, inicio, fim, largura, caractere)],
    metadados = data.table::data.table(
      ano = ano, arquivo_dados = normalizePath(arq_dados, winslash = "/"),
      arquivo_input = normalizePath(arq_input, winslash = "/"),
      tamanho_dados_bytes = file.info(arq_dados)$size,
      linhas_importadas = nrow(d), linhas_base_ampla = nrow(base)
    )
  )
}


# 4. PROCESSAMENTO PLURIANUAL -------------------------------------------------


resultados <- lapply(anos, processar_ano)
names(resultados) <- as.character(anos)


serie_totais <- data.table::rbindlist(lapply(resultados, `[[`, "totais"), fill = TRUE)
serie_detalhe <- data.table::rbindlist(lapply(resultados, `[[`, "detalhe"), fill = TRUE)
serie_formalidade <- data.table::rbindlist(lapply(resultados, `[[`, "formalidade"), fill = TRUE)
diagnostico_imputacao <- data.table::rbindlist(lapply(resultados, `[[`, "diagnostico"), fill = TRUE)
layouts_utilizados <- data.table::rbindlist(lapply(resultados, `[[`, "layout"), fill = TRUE)
metadados_execucao <- data.table::rbindlist(lapply(resultados, `[[`, "metadados"), fill = TRUE)


data.table::setcolorder(serie_totais, c("ano", "cenario", setdiff(names(serie_totais), c("ano", "cenario"))))
data.table::setorder(serie_totais, ano, cenario)
data.table::setorder(serie_detalhe, ano, cenario, ocupacao, posicao)
data.table::setorder(serie_formalidade, ano, cenario, formalidade)


# 5. VALIDACOES ENTRE CENARIOS E ANOS ----------------------------------------


checagem <- data.table::dcast(serie_totais, ano ~ cenario,
                              value.var = c("observacoes", "pessoas", "massa_anual"))
if (any(checagem$observacoes_amplo_5173_5174 < checagem$observacoes_estrito_5173) ||
    any(checagem$pessoas_amplo_5173_5174 < checagem$pessoas_estrito_5173) ||
    any(checagem$massa_anual_amplo_5173_5174 < checagem$massa_anual_estrito_5173)) {
  stop("Falha: algum total do cenario amplo ficou abaixo do estrito.")
}


if (!identical(sort(unique(serie_totais$ano)), anos)) {
  stop("Falha: a serie final nao contem exatamente os anos 2002-2009.")
}


# 6. EXPORTACAO ---------------------------------------------------------------


arquivos_saida <- c(
  serie_totais = file.path(pasta_saida, "pnad_2002_2009_totais_cenarios.csv"),
  detalhe = file.path(pasta_saida, "pnad_2002_2009_detalhe_ocupacao_posicao.csv"),
  formalidade = file.path(pasta_saida, "pnad_2002_2009_formalidade.csv"),
  imputacao = file.path(pasta_saida, "pnad_2002_2009_diagnostico_imputacao.csv"),
  layouts = file.path(pasta_saida, "pnad_2002_2009_layouts_utilizados.csv"),
  metadados = file.path(pasta_saida, "pnad_2002_2009_metadados_execucao.csv"),
  auditoria = file.path(pasta_saida, "pnad_2002_2009_auditoria.rds")
)


data.table::fwrite(serie_totais, arquivos_saida["serie_totais"], bom = TRUE)
data.table::fwrite(serie_detalhe, arquivos_saida["detalhe"], bom = TRUE)
data.table::fwrite(serie_formalidade, arquivos_saida["formalidade"], bom = TRUE)
data.table::fwrite(diagnostico_imputacao, arquivos_saida["imputacao"], bom = TRUE)
data.table::fwrite(layouts_utilizados, arquivos_saida["layouts"], bom = TRUE)
data.table::fwrite(metadados_execucao, arquivos_saida["metadados"], bom = TRUE)
saveRDS(list(
  parametros = list(anos = anos, ocupacoes_amplas = ocupacoes_amplas,
                    ocupacoes_estritas = ocupacoes_estritas,
                    posicoes_incluidas = posicoes_incluidas,
                    codigo_renda_ignorada = codigo_renda_ignorada,
                    anualizacao = 12L),
  serie_totais = serie_totais, serie_detalhe = serie_detalhe,
  serie_formalidade = serie_formalidade,
  diagnostico_imputacao = diagnostico_imputacao,
  layouts_utilizados = layouts_utilizados,
  metadados_execucao = metadados_execucao,
  checagem_cenarios = checagem,
  session_info = utils::sessionInfo()
), arquivos_saida["auditoria"])


message("\nProcessamento concluido sem falhas.")
message("Resultados gravados em: ", normalizePath(pasta_saida, winslash = "/"))
print(serie_totais)


})


# PNAD ANUAL 2011 ------------------------------------------------------------
local({
# ============================================================================
# PNAD 2011 — SEGURANÇA PRIVADA
# Script completo: importação, limpeza, estimação e exportação dos resultados
# ============================================================================
#
# OBJETIVO
# --------
# Estimar, a partir da PNAD 2011, o número de pessoas ocupadas, a renda média
# mensal e a massa de rendimentos do trabalho em ocupações relacionadas à
# segurança privada.
#
# O script produz dois cenários:
#
#   1. Amplo:   CBO-Domiciliar 5173 e 5174;
#   2. Estrito: CBO-Domiciliar 5173.
#
# Em ambos os cenários, são mantidas somente as seguintes posições na ocupação:
#
#   01 — empregado com carteira de trabalho assinada;
#   04 — outro empregado sem carteira de trabalho assinada;
#   09 — trabalhador por conta própria;
#   10 — empregador.
#
# São excluídos, entre outros, funcionários públicos estatutários (código 03),
# para evitar incorporar trabalhadores da segurança pública ao gasto privado.
#
# UNIDADE DOS RESULTADOS
# ---------------------
# Os resultados monetários são:
#
#   * expressos em reais nominais de 2011;
#   * sem encargos trabalhistas;
#   * sem deflação para preços de outro ano;
#   * baseados no rendimento mensal do trabalho principal (V4718).
#
# A massa anual é obtida multiplicando a massa mensal por 12.
#
# IMPUTAÇÃO DE RENDIMENTO
# -----------------------
# O código especial 999999999999 da variável V4718 significa rendimento sem
# declaração e é convertido em NA. Para cada cenário, rendimentos ausentes são
# imputados pela média ponderada dos declarantes do mesmo grupo de:
#
#   ocupação (V9906) x posição na ocupação (V4706).
#
# O script interrompe a execução se algum grupo com rendimento ausente não
# possuir ao menos um declarante, evitando uma imputação silenciosa ou arbitrária.
#
# INSUMOS OFICIAIS NECESSÁRIOS
# ----------------------------
# Na pasta definida em `pasta_2011`, devem existir, mesmo que em subpastas:
#
#   * PES2011.txt          — microdados de pessoas da PNAD 2011;
#   * dicPNAD2011.RData    — dicionário oficial de leitura em R.
#
# O arquivo .RData deve conter o objeto `dicpes2011`, com as colunas:
# `inicio`, `cod`, `tamanho` e `desc`.
#
# DEPENDÊNCIA
# -----------
# Pacote `readr`. Caso não esteja instalado, execute uma única vez:
# install.packages("readr")
#
# ============================================================================




# 1. CONFIGURAÇÃO DO USUÁRIO -----------------------------------------------


# Alterar somente este caminho se a pasta estiver em outro local.
# Em caminhos do Windows no R, usar barras normais (/), e não barras invertidas.
pasta_2011 <- file.path(dir_pnad_antiga, "2011")


# Pasta em que serão gravados os resultados.
pasta_resultados <- file.path(dir_saida, "pnad_2011")




# 2. VERIFICAÇÕES INICIAIS -------------------------------------------------


if (!dir.exists(pasta_2011)) {
  stop(
    "A pasta informada em `pasta_2011` não existe: ",
    pasta_2011,
    call. = FALSE
  )
}


if (!requireNamespace("readr", quietly = TRUE)) {
  stop(
    paste0(
      "O pacote `readr` não está instalado. Instale-o com ",
      "install.packages(\"readr\") e execute o script novamente."
    ),
    call. = FALSE
  )
}


dir.create(
  path = pasta_resultados,
  recursive = TRUE,
  showWarnings = FALSE
)




# 3. LOCALIZAÇÃO AUTOMÁTICA DOS INSUMOS -----------------------------------


arquivos_2011 <- list.files(
  path = pasta_2011,
  recursive = TRUE,
  full.names = TRUE
)


arquivo_pessoas_2011 <- arquivos_2011[
  grepl("^PES2011\\.txt$", basename(arquivos_2011), ignore.case = TRUE)
]


arquivo_dicionario_2011 <- arquivos_2011[
  grepl("^dicPNAD2011\\.RData$", basename(arquivos_2011), ignore.case = TRUE)
]


if (length(arquivo_pessoas_2011) != 1L) {
  stop(
    "Era esperado exatamente um arquivo PES2011.txt, mas foram encontrados ",
    length(arquivo_pessoas_2011), ".",
    call. = FALSE
  )
}


if (length(arquivo_dicionario_2011) != 1L) {
  stop(
    paste0(
      "Era esperado exatamente um arquivo dicPNAD2011.RData, mas foram ",
      "encontrados ", length(arquivo_dicionario_2011), "."
    ),
    call. = FALSE
  )
}


message("Microdados: ", arquivo_pessoas_2011)
message("Dicionário: ", arquivo_dicionario_2011)




# 4. LEITURA E VALIDAÇÃO DO DICIONÁRIO OFICIAL ----------------------------


# O arquivo é carregado em ambiente isolado para não sobrescrever objetos que
# eventualmente existam no ambiente global do usuário.
ambiente_dicionario <- new.env(parent = emptyenv())


objetos_carregados <- load(
  file = arquivo_dicionario_2011,
  envir = ambiente_dicionario
)


if (!"dicpes2011" %in% objetos_carregados) {
  stop(
    "O objeto `dicpes2011` não foi encontrado no dicionário oficial.",
    call. = FALSE
  )
}


dic_2011 <- get("dicpes2011", envir = ambiente_dicionario)


colunas_dicionario <- c("inicio", "cod", "tamanho", "desc")


if (!is.data.frame(dic_2011) ||
    !all(colunas_dicionario %in% names(dic_2011))) {
  stop(
    paste0(
      "O objeto `dicpes2011` não possui a estrutura esperada. ",
      "Colunas necessárias: ", paste(colunas_dicionario, collapse = ", "), "."
    ),
    call. = FALSE
  )
}


dic_2011$cod <- trimws(dic_2011$cod)


# A descrição usa codificação antiga. A conversão serve apenas para tornar
# textos de diagnóstico legíveis; posições, códigos e tamanhos não são alterados.
dic_2011$desc <- iconv(
  dic_2011$desc,
  from = "latin1",
  to = "UTF-8",
  sub = ""
)




# 5. SELEÇÃO DAS VARIÁVEIS -------------------------------------------------


# Identificação e características pessoais são mantidas para auditoria. As
# demais variáveis permitem definir ocupação, vínculo, rendimento e peso.
variaveis_necessarias <- c(
  "V0101", # ano de referência
  "V0102", # número de controle (os dois primeiros dígitos identificam a UF)
  "V0103", # número de série
  "V0301", # número de ordem da pessoa
  "V0302", # sexo
  "V8005", # idade
  "V9001", # trabalhou na semana de referência
  "V9002", # produção para o próprio consumo
  "V9003", # construção para o próprio uso
  "V9906", # código de ocupação no trabalho principal
  "V9907", # código de atividade no trabalho principal
  "V4704", # condição de atividade/ocupação
  "V4706", # posição na ocupação no trabalho principal
  "V4707", # faixa de horas em todos os trabalhos
  "V4718", # rendimento mensal do trabalho principal
  "V4719", # rendimento mensal de todos os trabalhos
  "V4720", # rendimento mensal de todas as fontes
  "V4729"  # peso da pessoa
)


variaveis_ausentes <- setdiff(variaveis_necessarias, dic_2011$cod)


if (length(variaveis_ausentes) > 0L) {
  stop(
    "Variáveis ausentes no dicionário: ",
    paste(variaveis_ausentes, collapse = ", "),
    call. = FALSE
  )
}


layout_necessario <- dic_2011[
  dic_2011$cod %in% variaveis_necessarias,
  colunas_dicionario,
  drop = FALSE
]


layout_necessario <- layout_necessario[
  order(layout_necessario$inicio),
  ,
  drop = FALSE
]


row.names(layout_necessario) <- NULL


if (nrow(layout_necessario) != length(variaveis_necessarias) ||
    anyDuplicated(layout_necessario$cod)) {
  stop(
    "O layout contém variáveis duplicadas ou número inesperado de linhas.",
    call. = FALSE
  )
}




# 6. IMPORTAÇÃO DO ARQUIVO DE LARGURA FIXA --------------------------------


posicoes_fixas <- readr::fwf_positions(
  start = layout_necessario$inicio,
  end = layout_necessario$inicio + layout_necessario$tamanho - 1L,
  col_names = layout_necessario$cod
)


# Todas as colunas são inicialmente lidas como texto. Isso preserva zeros à
# esquerda nos códigos e impede conversões automáticas indesejadas.
pnad_2011 <- readr::read_fwf(
  file = arquivo_pessoas_2011,
  col_positions = posicoes_fixas,
  col_types = readr::cols(.default = readr::col_character()),
  trim_ws = TRUE,
  progress = interactive(),
  show_col_types = FALSE
)


if (nrow(pnad_2011) != 358919L) {
  warning(
    "A base possui ", nrow(pnad_2011),
    " linhas; a leitura anteriormente validada possuía 358.919."
  )
}


if (!identical(names(pnad_2011), layout_necessario$cod)) {
  stop("Os nomes ou a ordem das colunas importadas são inesperados.", call. = FALSE)
}




# 7. PADRONIZAÇÃO E LIMPEZA ------------------------------------------------


# A UF é identificada pelos dois primeiros dígitos do número de controle.
pnad_2011$UF <- substr(pnad_2011$V0102, 1L, 2L)


# Apenas variáveis quantitativas são convertidas para número. Variáveis que
# representam códigos permanecem como texto.
variaveis_numericas <- c("V8005", "V4718", "V4719", "V4720", "V4729")


pnad_2011[variaveis_numericas] <- lapply(
  pnad_2011[variaveis_numericas],
  function(x) suppressWarnings(as.numeric(x))
)


# V4718 é a medida de rendimento empregada na estimação.
pnad_2011$rendimento_principal <- pnad_2011$V4718


# Na PNAD 2011, 999999999999 representa rendimento sem declaração.
pnad_2011$rendimento_principal[
  !is.na(pnad_2011$rendimento_principal) &
    pnad_2011$rendimento_principal >= 999999999999
] <- NA_real_




# 8. DEFINIÇÕES ANALÍTICAS -------------------------------------------------


posicoes_seguranca_privada <- c("01", "04", "09", "10")


cenarios <- list(
  amplo_5173_5174 = c("5173", "5174"),
  estrito_5173 = "5173"
)


# Classificação usada na apresentação dos resultados. Somente o código 01 é
# tratado como emprego formal com carteira; 04, 09 e 10 são agregados em
# "demais posições".
classificar_formalidade <- function(posicao) {
  ifelse(
    posicao == "01",
    "formal_com_carteira",
    "demais_posicoes"
  )
}




# 9. FUNÇÃO DE ESTIMAÇÃO ---------------------------------------------------


estimar_cenario <- function(dados, ocupacoes, nome_cenario) {


  filtro <-
    !is.na(dados$V4704) & dados$V4704 == "1" &
    !is.na(dados$V9906) & dados$V9906 %in% ocupacoes &
    !is.na(dados$V4706) & dados$V4706 %in% posicoes_seguranca_privada &
    !is.na(dados$V4729) & dados$V4729 > 0


  base <- as.data.frame(dados[which(filtro), , drop = FALSE])


  if (nrow(base) == 0L) {
    stop("O cenário `", nome_cenario, "` não possui observações.", call. = FALSE)
  }


  base$cenario <- nome_cenario
  base$formalidade <- classificar_formalidade(base$V4706)
  base$rendimento_imputado <- base$rendimento_principal
  base$rendimento_foi_imputado <- is.na(base$rendimento_principal)


  chave_grupo <- interaction(
    base$V9906,
    base$V4706,
    drop = TRUE,
    sep = "_"
  )


  indices_por_grupo <- split(seq_len(nrow(base)), chave_grupo)
  diagnosticos <- vector("list", length(indices_por_grupo))
  names(diagnosticos) <- names(indices_por_grupo)


  for (nome_grupo in names(indices_por_grupo)) {
    indice <- indices_por_grupo[[nome_grupo]]
    rendimento <- base$rendimento_principal[indice]
    peso <- base$V4729[indice]
    declarado <- !is.na(rendimento)


    if (!any(declarado)) {
      stop(
        "Não há declarante de rendimento no grupo ", nome_grupo,
        " do cenário ", nome_cenario, ".",
        call. = FALSE
      )
    }


    media_ponderada <- stats::weighted.mean(
      x = rendimento[declarado],
      w = peso[declarado],
      na.rm = TRUE
    )


    base$rendimento_imputado[indice[!declarado]] <- media_ponderada


    diagnosticos[[nome_grupo]] <- data.frame(
      cenario = nome_cenario,
      ocupacao = base$V9906[indice[1L]],
      posicao = base$V4706[indice[1L]],
      observacoes_amostrais = length(indice),
      observacoes_sem_rendimento = sum(!declarado),
      percentual_amostral_imputado = 100 * mean(!declarado),
      pessoas_representadas = sum(peso),
      media_ponderada_declarantes = media_ponderada,
      stringsAsFactors = FALSE
    )
  }


  diagnostico_grupos <- do.call(rbind, diagnosticos)
  row.names(diagnostico_grupos) <- NULL


  if (anyNA(base$rendimento_imputado)) {
    stop(
      "Ainda existem rendimentos ausentes após a imputação no cenário `",
      nome_cenario, "`.",
      call. = FALSE
    )
  }


  # Contribuição de cada registro para as estimativas populacionais.
  base$pessoas_ponderadas <- base$V4729
  base$massa_salarial_mensal_ponderada <-
    base$rendimento_imputado * base$V4729


  # Agregação por formalidade.
  grupos_formalidade <- split(
    seq_len(nrow(base)),
    base$formalidade,
    drop = TRUE
  )


  resultado_formalidade <- do.call(
    rbind,
    lapply(names(grupos_formalidade), function(grupo) {
      indice <- grupos_formalidade[[grupo]]
      pessoas <- sum(base$pessoas_ponderadas[indice])
      massa_mensal <- sum(base$massa_salarial_mensal_ponderada[indice])


      data.frame(
        cenario = nome_cenario,
        formalidade = grupo,
        observacoes_amostrais = length(indice),
        pessoas_ocupadas = pessoas,
        renda_media_mensal = massa_mensal / pessoas,
        massa_salarial_mensal = massa_mensal,
        massa_salarial_anual = 12 * massa_mensal,
        stringsAsFactors = FALSE
      )
    })
  )


  row.names(resultado_formalidade) <- NULL


  pessoas_total <- sum(base$pessoas_ponderadas)
  massa_mensal_total <- sum(base$massa_salarial_mensal_ponderada)


  resultado_total <- data.frame(
    ano = 2011L,
    cenario = nome_cenario,
    ocupacoes_incluidas = paste(ocupacoes, collapse = "+"),
    observacoes_amostrais = nrow(base),
    observacoes_com_renda_imputada = sum(base$rendimento_foi_imputado),
    pessoas_ocupadas = pessoas_total,
    renda_media_mensal = massa_mensal_total / pessoas_total,
    massa_salarial_mensal_reais_nominais = massa_mensal_total,
    massa_salarial_anual_reais_nominais = 12 * massa_mensal_total,
    massa_salarial_anual_bilhoes_nominais = 12 * massa_mensal_total / 1e9,
    precos = "reais nominais de 2011",
    encargos_trabalhistas_incluidos = FALSE,
    stringsAsFactors = FALSE
  )


  list(
    base_analitica = base,
    diagnostico_grupos = diagnostico_grupos,
    resultado_formalidade = resultado_formalidade,
    resultado_total = resultado_total
  )
}




# 10. ESTIMAÇÃO DOS DOIS CENÁRIOS -----------------------------------------


resultados <- lapply(
  names(cenarios),
  function(nome) {
    estimar_cenario(
      dados = pnad_2011,
      ocupacoes = cenarios[[nome]],
      nome_cenario = nome
    )
  }
)


names(resultados) <- names(cenarios)


resultado_final_2011 <- do.call(
  rbind,
  lapply(resultados, `[[`, "resultado_total")
)


resultado_por_formalidade_2011 <- do.call(
  rbind,
  lapply(resultados, `[[`, "resultado_formalidade")
)


diagnostico_imputacao_2011 <- do.call(
  rbind,
  lapply(resultados, `[[`, "diagnostico_grupos")
)


row.names(resultado_final_2011) <- NULL
row.names(resultado_por_formalidade_2011) <- NULL
row.names(diagnostico_imputacao_2011) <- NULL




# 11. VALIDAÇÕES FINAIS ----------------------------------------------------


# A leitura já validada indicou 2.840 observações no cenário amplo:
# 5173: 1.154 (01) + 111 (04) + 3 (09) = 1.268;
# 5174: 1.376 (01) + 251 (04) + 64 (09) + 1 (10) = 1.692.
n_amplo <- resultados$amplo_5173_5174$resultado_total$observacoes_amostrais


if (n_amplo != 2840L) {
  warning(
    "O cenário amplo contém ", n_amplo,
    " observações, em vez das 2.840 anteriormente validadas."
  )
}


if (any(!is.finite(resultado_final_2011$massa_salarial_anual_reais_nominais)) ||
    any(resultado_final_2011$massa_salarial_anual_reais_nominais <= 0)) {
  stop("Foram obtidos totais anuais inválidos.", call. = FALSE)
}


# Confere se a soma das categorias de formalidade reproduz o total do cenário.
for (nome in names(cenarios)) {
  total_formalidade <- sum(
    resultado_por_formalidade_2011$massa_salarial_anual[
      resultado_por_formalidade_2011$cenario == nome
    ]
  )


  total_cenario <- resultado_final_2011$massa_salarial_anual_reais_nominais[
    resultado_final_2011$cenario == nome
  ]


  if (!isTRUE(all.equal(total_formalidade, total_cenario, tolerance = 1e-8))) {
    stop(
      "A soma por formalidade não reproduz o total do cenário `",
      nome, "`.",
      call. = FALSE
    )
  }
}




# 12. EXPORTAÇÃO -----------------------------------------------------------


# UTF-8 com BOM facilita a abertura dos CSVs no Excel em português.
readr::write_excel_csv(
  resultado_final_2011,
  file.path(pasta_resultados, "pnad_2011_resultado_final_cenarios.csv"),
  na = ""
)


readr::write_excel_csv(
  resultado_por_formalidade_2011,
  file.path(pasta_resultados, "pnad_2011_resultado_por_formalidade.csv"),
  na = ""
)


readr::write_excel_csv(
  diagnostico_imputacao_2011,
  file.path(pasta_resultados, "pnad_2011_diagnostico_imputacao.csv"),
  na = ""
)


# O arquivo RDS preserva todos os objetos analíticos e tipos de variáveis para
# auditoria posterior, sem a perda de precisão que pode ocorrer em planilhas.
saveRDS(
  object = list(
    metadados = list(
      ano = 2011L,
      fonte = "PNAD 2011/IBGE",
      arquivo_pessoas = arquivo_pessoas_2011,
      arquivo_dicionario = arquivo_dicionario_2011,
      data_execucao = Sys.time(),
      observacao = paste(
        "Valores nominais de 2011, sem encargos e sem deflação;",
        "renda ausente imputada por ocupação x posição."
      )
    ),
    layout_utilizado = layout_necessario,
    resultados = resultados,
    resultado_final = resultado_final_2011,
    resultado_por_formalidade = resultado_por_formalidade_2011,
    diagnostico_imputacao = diagnostico_imputacao_2011
  ),
  file = file.path(pasta_resultados, "pnad_2011_resultados_completos.rds")
)




# 13. APRESENTAÇÃO NO CONSOLE ---------------------------------------------


message("\nProcessamento concluído com sucesso.")
message("Resultados gravados em: ", pasta_resultados, "\n")


print(resultado_final_2011, row.names = FALSE)


message("\nResultado por formalidade:")
print(resultado_por_formalidade_2011, row.names = FALSE)


message("\nDiagnóstico da imputação por ocupação x posição:")
print(diagnostico_imputacao_2011, row.names = FALSE)




# FIM DO SCRIPT ------------------------------------------------------------


})


# PNAD CONTINUA 2012-2025 ----------------------------------------------------
local({
library(PNADcIBGE)
library(dplyr)
library(survey)
library(purrr)
library(writexl)


# =========================================================
# 1. DEFINIR ANOS
# =========================================================


anos = 2012:2025


# =========================================================
# 2. FUNÇÃO PARA DEFINIR ENTREVISTA
# =========================================================


definir_entrevista = function(ano){
  
  if(ano %in% c(2020, 2021)){
    
    return(5)
    
  } else {
    
    return(1)
    
  }
  
}


# =========================================================
# 3. FUNÇÃO PRINCIPAL
# =========================================================


processar_pnad = function(pnadc, ano){
  
  # =====================================================
  # 3.1 CRIAR INDICADORES DE OCUPAÇÃO
  # =====================================================
  
  pnadc =
    update(
      
      pnadc,
      
      # -------------------------------------------------
      # TRABALHO PRINCIPAL
      # -------------------------------------------------
      
      principal_conservador =
        ifelse(
          !is.na(V4010) & V4010 == "5414",
          1,
          0
        ),
      
      principal_ampliado =
        ifelse(
          V4010 %in% c("5414", "5419"),
          1,
          0
        ),
      
      # -------------------------------------------------
      # TRABALHO SECUNDÁRIO
      # -------------------------------------------------
      
      secundario_conservador =
        ifelse(
          !is.na(V4041) & V4041 == "5414",
          1,
          0
        ),
      
      secundario_ampliado =
        ifelse(
          V4041 %in% c("5414", "5419"),
          1,
          0
        )
    )
  
  # =====================================================
  # 3.2 FORMALIDADE
  # =====================================================
  
  pnadc =
    update(
      
      pnadc,
      
      # -------------------------------------------------
      # FORMALIDADE - TRABALHO PRINCIPAL
      # -------------------------------------------------
      
      principal_formal =
        ifelse(
          (!is.na(V4029) & V4029 == "1") |
            (!is.na(V4019) & V4019 == "1"),
          1,
          0
        ),
      
      principal_informal =
        ifelse(
          (!is.na(V4029) & V4029 == "2") |
            (!is.na(V4019) & V4019 == "2"),
          1,
          0
        ),
      
      # -------------------------------------------------
      # FORMALIDADE - TRABALHO SECUNDÁRIO
      # -------------------------------------------------
      
      secundario_formal =
        ifelse(
          (!is.na(V4048) & V4048 == "1") |
            (!is.na(V4046) & V4046 == "1"),
          1,
          0
        ),
      
      secundario_informal =
        ifelse(
          (!is.na(V4048) & V4048 == "2") |
            (!is.na(V4046) & V4046 == "2"),
          1,
          0
        )
    )
  
  # =====================================================
  # 3.3 POSTOS DE TRABALHO
  # =====================================================
  
  pnadc =
    update(
      
      pnadc,
      
      conservador_formal =
        principal_conservador * principal_formal +
        secundario_conservador * secundario_formal,
      
      conservador_informal =
        principal_conservador * principal_informal +
        secundario_conservador * secundario_informal,
      
      conservador_total =
        principal_conservador +
        secundario_conservador,
      
      ampliado_formal =
        principal_ampliado * principal_formal +
        secundario_ampliado * secundario_formal,
      
      ampliado_informal =
        principal_ampliado * principal_informal +
        secundario_ampliado * secundario_informal,
      
      ampliado_total =
        principal_ampliado +
        secundario_ampliado
    )
  
  # =====================================================
  # 3.4 RENDIMENTOS DEFLACIONADOS
  # =====================================================
  
  pnadc =
    update(
      
      pnadc,
      
      renda_principal =
        as.numeric(V403312) * CO2,
      
      renda_secundaria =
        as.numeric(V405012) * CO2
    )
  
  # =====================================================
  # 3.5 MASSA SALARIAL
  # =====================================================
  
  pnadc =
    update(
      
      pnadc,
      
      # -------------------------------------------------
      # CENÁRIO CONSERVADOR
      # -------------------------------------------------
      
      renda_conservador_formal =
        
        ifelse(
          principal_conservador == 1 &
            principal_formal == 1,
          
          renda_principal,
          
          0
        ) +
        
        ifelse(
          secundario_conservador == 1 &
            secundario_formal == 1,
          
          renda_secundaria,
          
          0
        ),
      
      renda_conservador_informal =
        
        ifelse(
          principal_conservador == 1 &
            principal_informal == 1,
          
          renda_principal,
          
          0
        ) +
        
        ifelse(
          secundario_conservador == 1 &
            secundario_informal == 1,
          
          renda_secundaria,
          
          0
        ),
      
      renda_conservador_total =
        
        ifelse(
          principal_conservador == 1,
          
          renda_principal,
          
          0
        ) +
        
        ifelse(
          secundario_conservador == 1,
          
          renda_secundaria,
          
          0
        ),
      
      # -------------------------------------------------
      # CENÁRIO AMPLIADO
      # -------------------------------------------------
      
      renda_ampliado_formal =
        
        ifelse(
          principal_ampliado == 1 &
            principal_formal == 1,
          
          renda_principal,
          
          0
        ) +
        
        ifelse(
          secundario_ampliado == 1 &
            secundario_formal == 1,
          
          renda_secundaria,
          
          0
        ),
      
      renda_ampliado_informal =
        
        ifelse(
          principal_ampliado == 1 &
            principal_informal == 1,
          
          renda_principal,
          
          0
        ) +
        
        ifelse(
          secundario_ampliado == 1 &
            secundario_informal == 1,
          
          renda_secundaria,
          
          0
        ),
      
      renda_ampliado_total =
        
        ifelse(
          principal_ampliado == 1,
          
          renda_principal,
          
          0
        ) +
        
        ifelse(
          secundario_ampliado == 1,
          
          renda_secundaria,
          
          0
        )
    )
  
  # =====================================================
  # 3.6 ESTIMAR RESULTADOS
  # =====================================================
  
  resultados =
    svytotal(
      
      ~conservador_formal +
        conservador_informal +
        conservador_total +
        
        ampliado_formal +
        ampliado_informal +
        ampliado_total +
        
        renda_conservador_formal +
        renda_conservador_informal +
        renda_conservador_total +
        
        renda_ampliado_formal +
        renda_ampliado_informal +
        renda_ampliado_total,
      
      pnadc,
      
      na.rm = TRUE
    )
  
  # =====================================================
  # 3.7 EXTRAIR ESTIMATIVAS
  # =====================================================
  
  estimativas =
    as.data.frame(coef(resultados))
  
  ic =
    as.data.frame(confint(resultados))
  
  # =====================================================
  # 3.8 ORGANIZAR RESULTADOS
  # =====================================================
  
  tabela_final =
    tibble(
      
      variavel = rownames(estimativas),
      
      valor = estimativas[[1]],
      
      ic_min = ic[[1]],
      
      ic_max = ic[[2]]
      
    )
  
  tabela_final =
    tabela_final %>%
    
    mutate(
      ano = ano
    )
  
  return(tabela_final)
  
}


# O teste interativo de 2016 foi removido da versão de publicação.


# =========================================================
# 5. RODAR TODOS OS ANOS
# =========================================================


lista_resultados = list()


for(ano in anos){
  
  cat("\n")
  cat("Processando ano:", ano, "\n")
  
  entrevista = definir_entrevista(ano)
  
  pnad =
    PNADcIBGE::get_pnadc(
      year = ano,
      interview = entrevista,
      labels = FALSE,
      deflator = TRUE,
      design = TRUE
    )
  
  lista_resultados[[as.character(ano)]] =
    processar_pnad(pnad, ano)
  
}


# =========================================================
# 6. JUNTAR RESULTADOS
# =========================================================


base_final =
  bind_rows(lista_resultados)


# =========================================================
# 7. EXPORTAR
# =========================================================




# =========================================================
# 6. ORGANIZAR E EXPORTAR
# =========================================================
base_final_wide <- base_final %>%
  tidyr::pivot_wider(
    id_cols = ano,
    names_from = variavel,
    values_from = c(valor, ic_min, ic_max),
    names_glue = "{variavel}_{.value}"
  ) %>%
  arrange(ano)


writexl::write_xlsx(
  list(resultados_longos = base_final, resultados_anuais = base_final_wide),
  file.path(dir_saida, "seguranca_privada_pnadc_2012_2025.xlsx")
)


})
