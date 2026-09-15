# ==============================================================================
# 05 — PROCESSOS JUDICIAIS
# Projeto: Custos da Criminalidade no Brasil, 1996-2025
# ==============================================================================
# Escopo deste arquivo
# Organiza as etapas executadas no R para participação criminal do Ministério Público e quantidades processuais utilizadas na estimativa da defesa. As reconstruções históricas, imputações, honorários, deflação e consolidação financeira permanecem na planilha final.
#
# Reprodutibilidade
# 1. Ajuste somente os caminhos em "CONFIGURACAO".
# 2. Instale previamente os pacotes listados; o script não instala pacotes.
# 3. As etapas feitas em Excel são identificadas e não são recriadas aqui.
# 4. As saídas são gravadas em dir_saida sem chamadas interativas.
# ==============================================================================


options(stringsAsFactors = FALSE, survey.lonely.psu = "adjust")


# CONFIGURACAO ---------------------------------------------------------------
dir_dados_mp <- "dados/processos_judiciais/mp"
arquivo_base_tj <- "dados/processos_judiciais/base_tj.csv"
arquivo_dicionario_tj <- "dados/processos_judiciais/dicionario_variaveis.csv"
dir_saida <- "resultados/processos_judiciais"
dir.create(dir_saida, recursive = TRUE, showWarnings = FALSE)


pacotes <- c("dplyr","stringr","stringi","tidyr","tidytext","readr","scales")
faltantes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]
if (length(faltantes)) stop("Instale os pacotes: ", paste(faltantes, collapse = ", "))






# Parte 1 - Tribunais de Justiça: Quanto do orçamento dos Tribunais de 
# Justiça pertence ao direito penal?


# Parte 2 - Ministério Público: Quanto do orçamento do Ministério 
# Público pertence ao direito penal?


# Parte 3 - Defesa: Aqui a lógica muda, dado que existe um orçamento 
# nacional da advocacia. Então eles fazem uma pergunta: 
# Quanto custa, em média, defender um processo criminal?




# ================================================
# Eixo B: Ministério Público
# ================================================




# 1. Definir o caminho da pasta (com barras invertidas duplicadas ou barras normais)
caminho_pasta <- dir_dados_mp


# Listar todos os arquivos .csv dentro da pasta (com o caminho completo)
arquivos <- list.files(path = caminho_pasta, pattern = "\\.csv$", full.names = TRUE)


# Loop para processar cada um dos 24 arquivos
for (arquivo in arquivos) {
  
  # Extrair apenas o nome do arquivo (sem o ".csv" e sem o caminho da pasta)
  nome_objeto <- tools::file_path_sans_ext(basename(arquivo))
  
  # (Tarefa 1) Ler o arquivo e criar o objeto no RStudio com o nome original
  dados <- read.csv(arquivo, stringsAsFactors = FALSE) # Ajuste para read.csv2 se o separador for ponto e vírgula
  assign(nome_objeto, dados, envir = environment())
  
  # Imprimir o nome do objeto atual para organizar a visualização no console
  cat("\n========================================================\n")
  cat("PROCESSANDO O OBJETO:", nome_objeto, "\n")
  cat("========================================================\n")
  
  # (Tarefa 2) Rodar o head nas primeiras linhas do objeto criado
  cat("--- Primeiras linhas (head) ---\n")
  print(head(dados))
  
  # (Tarefa 3) Rodar o unique na coluna "Indicador"
  cat("\n--- Valores únicos da coluna 'Indicador' ---\n")
  if ("Indicador" %in% colnames(dados)) {
    print(unique(dados$Indicador))
  } else {
    cat("Aviso: A coluna 'Indicador' não foi encontrada neste arquivo.\n")
  }
}




# 1. Criar uma função para extrair "RECEBIDOS"




recebidos <- function(base){
  
  base %>%
    
    filter(grepl("^RECEBIDOS", Indicador)) %>%
    
    summarise(
      
      total = sum(
        parse_number(Ocorrências),
        na.rm = TRUE
      )
      
    ) %>%
    
    pull(total)
  
}




# 2. Calcular totais de cada anexo


r_1a <- recebidos(anexo_1a)
r_1b <- recebidos(anexo_1b)
r_1c <- recebidos(anexo_1c)
r_1d <- recebidos(anexo_1d)


r_2a <- recebidos(anexo_2a)
r_2b <- recebidos(anexo_2b)
r_2c <- recebidos(anexo_2c)
r_2d <- recebidos(anexo_2d)


r_3 <- recebidos(anexo_3)


r_4b <- recebidos(anexo_4b)
r_4c <- recebidos(anexo_4c)


r_5a <- recebidos(anexo_5a)
r_5b <- recebidos(anexo_5b)


r_8 <- recebidos(anexo_8)




# 3. Total Criminal


criminal <-
  
  r_2a +
  r_2b +
  r_2c +
  r_2d


# 4. Total Geral da atuação funcional


total <-
  
  r_1a +
  r_1b +
  r_1c +
  r_1d +
  
  r_2a +
  r_2b +
  r_2c +
  r_2d +
  
  r_3 +
  
  r_4b +
  r_4c +
  
  r_5a +
  r_5b +
  
  r_8


# 5. Fração criminal


fracao_criminal <- criminal / total


# 6. Exibir o resultado


cat(
  "Participação da atuação criminal:",
  scales::percent(fracao_criminal, accuracy = 0.01)
)






# ================================================
# Eixo C: Defesa
# ================================================


## 1. Importar dados dos Tribunais de Justiça (TJs):


caminho <- arquivo_base_tj
dados_tj = read.csv(caminho, check.names = FALSE)


## 2. Importar dicionário de variáveis para dados_tj:


caminho <- arquivo_dicionario_tj
dicionario_tj = read.csv(caminho, check.names = FALSE)




## 3. Quantidade de serviços de defesa na Justiça Estadual


# a) Definir os 27 Tribunais de Justiça estaduais


tjs_estaduais = c(
  
  "TJAC", "TJAL", "TJAP", "TJAM", "TJBA", "TJCE", "TJDFT", "TJES", 
  "TJGO", "TJMA", "TJMT", "TJMS", "TJMG", "TJPA", "TJPB", "TJPR", 
  "TJPE", "TJPI", "TJRJ", "TJRN", "TJRS", "TJRO", "TJRR", "TJSC",
  "TJSP", "TJSE", "TJTO")


# b) Selecionar os TJs estaduais e o período do projeto


base_defesa_ufs = dados_tj %>%
  
  filter(sigla %in% tjs_estaduais,
    
    ano >= 2009,
    
    ano <= 2025)


# c) Conferir número de TJs por ano


base_defesa_ufs %>% group_by(ano) %>%
  
  summarise(numero_tjs = n_distinct(sigla),
    
    observacoes = n(),
    
    .groups = "drop")




# d) Verificar duplicidades por TJ e ano


duplicidades = base_defesa_ufs %>%
  
  count(sigla, ano, name = "n") %>%
  
  filter(n > 1)


duplicidades




# e) Converter variáveis processuais para formato numérico


base_defesa_ufs = base_defesa_ufs %>%
  
  mutate(
    
    processos_comuns = as.numeric(na_if(trimws(tolower(cnccrim1)),
          "nd")),
    
    processos_jecrim = as.numeric(na_if(trimws(tolower(cnccrimje)),
          
          "nd")))


# f) Criar indicadores de disponibilidade dos dados


base_defesa_ufs = base_defesa_ufs %>%
  
  mutate(
    
    disponivel_comum =
      !is.na(processos_comuns),
    
    disponivel_jecrim =
      !is.na(processos_jecrim),
    
    numero_componentes_disponiveis =
      as.integer(disponivel_comum) +
      as.integer(disponivel_jecrim))


# g) Classificar a cobertura da quantidade de serviços


base_defesa_ufs = base_defesa_ufs %>%
  
  mutate(
    
    cobertura_servicos_defesa =
      case_when(
        
        disponivel_comum &
          disponivel_jecrim ~
          "Completa",
        
        disponivel_comum &
          !disponivel_jecrim ~
          "Somente processo comum",
        
        !disponivel_comum &
          disponivel_jecrim ~
          "Somente Juizado Especial Criminal",
        
        TRUE ~
          "Sem informação"
        
      )
    
  )


# h) Construir a quantidade observada de serviços de defesa


base_defesa_ufs <- base_defesa_ufs %>%
  
  mutate(
    
    quantidade_servicos_defesa =
      case_when(
        
        cobertura_servicos_defesa == "Completa" ~
          processos_comuns +
          processos_jecrim,
        
        TRUE ~
          NA_real_
        
      )
    
  )


# i) Construir uma medida parcial para diagnóstico


base_defesa_ufs <- base_defesa_ufs %>%
  
  mutate(
    
    quantidade_servicos_defesa_parcial =
      case_when(
        
        numero_componentes_disponiveis == 0 ~
          NA_real_,
        
        TRUE ~
          rowSums(
            
            across(
              
              c(
                processos_comuns,
                processos_jecrim
              )
              
            ),
            
            na.rm = TRUE
            
          )
        
      )
    
  )




# j) Diagnóstico anual da cobertura


cobertura_anual_defesa <- base_defesa_ufs %>%
  
  group_by(ano) %>%
  
  summarise(
    
    numero_tjs =
      n_distinct(sigla),
    
    cobertura_completa =
      sum(
        cobertura_servicos_defesa == "Completa"
      ),
    
    somente_processo_comum =
      sum(
        cobertura_servicos_defesa ==
          "Somente processo comum"
      ),
    
    somente_jecrim =
      sum(
        cobertura_servicos_defesa ==
          "Somente Juizado Especial Criminal"
      ),
    
    sem_informacao =
      sum(
        cobertura_servicos_defesa ==
          "Sem informação"
      ),
    
    processos_comuns_observados =
      sum(
        processos_comuns,
        na.rm = TRUE
      ),
    
    processos_jecrim_observados =
      sum(
        processos_jecrim,
        na.rm = TRUE
      ),
    
    quantidade_estrita =
      sum(
        quantidade_servicos_defesa,
        na.rm = TRUE
      ),
    
    quantidade_parcial =
      sum(
        quantidade_servicos_defesa_parcial,
        na.rm = TRUE
      ),
    
    .groups = "drop"
    
  )


print(
  cobertura_anual_defesa,
  n = Inf
)




# l) Diagnóstico da cobertura por Tribunal


cobertura_tj_defesa <- base_defesa_ufs %>%
  
  group_by(sigla) %>%
  
  summarise(
    
    anos_observados =
      n_distinct(ano),
    
    anos_cobertura_completa =
      sum(
        cobertura_servicos_defesa == "Completa"
      ),
    
    anos_somente_processo_comum =
      sum(
        cobertura_servicos_defesa ==
          "Somente processo comum"
      ),
    
    anos_somente_jecrim =
      sum(
        cobertura_servicos_defesa ==
          "Somente Juizado Especial Criminal"
      ),
    
    anos_sem_informacao =
      sum(
        cobertura_servicos_defesa ==
          "Sem informação"
      ),
    
    .groups = "drop"
    
  ) %>%
  
  arrange(
    
    anos_cobertura_completa,
    
    sigla
    
  )


print(
  cobertura_tj_defesa,
  n = Inf
)




# m) Construir o total nacional publicado pelo CNJ


total_nacional_cnj <- dados_tj %>%
  
  filter(
    
    sigla == "TJ",
    
    ano >= 2016,
    
    ano <= 2025
    
  ) %>%
  
  transmute(
    
    ano,
    
    processos_comuns_cnj =
      as.numeric(
        
        na_if(
          
          trimws(
            tolower(cnccrim1)
          ),
          
          "nd"
          
        )
        
      ),
    
    processos_jecrim_cnj =
      as.numeric(
        
        na_if(
          
          trimws(
            tolower(cnccrimje)
          ),
          
          "nd"
          
        )
        
      ),
    
    quantidade_servicos_defesa_cnj =
      processos_comuns_cnj +
      processos_jecrim_cnj
    
  )


# n) Comparar a soma das UFs com o agregado nacional


validacao_defesa <- base_defesa_ufs %>%
  
  group_by(ano) %>%
  
  summarise(
    
    processos_comuns_ufs =
      sum(
        processos_comuns,
        na.rm = TRUE
      ),
    
    processos_jecrim_ufs =
      sum(
        processos_jecrim,
        na.rm = TRUE
      ),
    
    quantidade_parcial_ufs =
      sum(
        quantidade_servicos_defesa_parcial,
        na.rm = TRUE
      ),
    
    ufs_completas =
      sum(
        cobertura_servicos_defesa == "Completa"
      ),
    
    .groups = "drop"
    
  ) %>%
  
  left_join(
    
    total_nacional_cnj,
    
    by = "ano"
    
  ) %>%
  
  mutate(
    
    cobertura_processos_comuns =
      processos_comuns_ufs /
      processos_comuns_cnj,
    
    cobertura_processos_jecrim =
      processos_jecrim_ufs /
      processos_jecrim_cnj,
    
    cobertura_total =
      quantidade_parcial_ufs /
      quantidade_servicos_defesa_cnj
    
  )


print(
  validacao_defesa,
  n = Inf
)


# o) Registrar a validação: 


validacao_defesa <- validacao_defesa %>%
  
  mutate(
    
    diferenca_processos_comuns =
      processos_comuns_ufs -
      processos_comuns_cnj,
    
    diferenca_processos_jecrim =
      processos_jecrim_ufs -
      processos_jecrim_cnj,
    
    diferenca_total =
      quantidade_parcial_ufs -
      quantidade_servicos_defesa_cnj,
    
    validacao_exata =
      diferenca_processos_comuns == 0 &
      diferenca_processos_jecrim == 0 &
      diferenca_total == 0
    
  )




# ============================================================
# Quantidade de serviços de defesa — 2009 a 2025
# ============================================================




# 1. Definir os 27 Tribunais de Justiça estaduais


tjs_estaduais <- c(
  
  "TJAC", "TJAL", "TJAP", "TJAM", "TJBA",
  "TJCE", "TJDFT", "TJES", "TJGO", "TJMA",
  "TJMT", "TJMS", "TJMG", "TJPA", "TJPB",
  "TJPR", "TJPE", "TJPI", "TJRJ", "TJRN",
  "TJRS", "TJRO", "TJRR", "TJSC", "TJSP",
  "TJSE", "TJTO"
  
)


# 2. Construir a base estadual de serviços de defesa


quantidade_servicos_defesa <- dados_tj %>%
  
  filter(
    
    sigla %in% tjs_estaduais,
    
    ano >= 2009,
    
    ano <= 2025
    
  ) %>%
  
  transmute(
    
    sigla,
    
    ano,
    
    processos_defesa_comum =
      as.numeric(
        
        na_if(
          
          trimws(
            tolower(cnccrim1)
          ),
          
          "nd"
          
        )
        
      ),
    
    processos_defesa_jecrim =
      as.numeric(
        
        na_if(
          
          trimws(
            tolower(cnccrimje)
          ),
          
          "nd"
          
        )
        
      )
    
  ) %>%
  
  mutate(
    
    quantidade_servicos_defesa =
      processos_defesa_comum +
      processos_defesa_jecrim
    
  ) %>%
  
  arrange(
    
    ano,
    
    sigla
    
  )


# 3. Construir a base nacional de serviços de defesa 


quantidade_servicos_defesa_brasil <-
  quantidade_servicos_defesa %>%
  
  group_by(ano) %>%
  
  summarise(
    
    processos_defesa_comum =
      sum(
        processos_defesa_comum
      ),
    
    processos_defesa_jecrim =
      sum(
        processos_defesa_jecrim
      ),
    
    quantidade_servicos_defesa =
      sum(
        quantidade_servicos_defesa
      ),
    
    .groups = "drop"
    
  ) %>%
  
  mutate(
    
    participacao_comum =
      processos_defesa_comum /
      quantidade_servicos_defesa,
    
    participacao_jecrim =
      processos_defesa_jecrim /
      quantidade_servicos_defesa
    
  )




## 4. Exportar tabelas: 


readr::write_csv(quantidade_servicos_defesa, file.path(dir_saida, "quantidade_servicos_defesa.csv"))
readr::write_csv(quantidade_servicos_defesa_brasil, file.path(dir_saida, "quantidade_servicos_defesa_brasil.csv"))
