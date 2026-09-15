# ==============================================================================
# 04 — SERVIÇOS MÉDICOS E RECUPERAÇÃO
# Projeto: Custos da Criminalidade no Brasil, 1996-2025
# ==============================================================================
# Escopo deste arquivo
# Reproduz as etapas executadas no R para o SIH/SUS de 2008-2025, inclusive seleção CID, custo hospitalar, perda produtiva temporária e imputação de setembro de 2009. A série histórica e a deflação de 1996-1997 foram tratadas fora do R e não são recalculadas aqui.
#
# Reprodutibilidade
# 1. Ajuste somente os caminhos em "CONFIGURACAO".
# 2. Instale previamente os pacotes listados; o script não instala pacotes.
# 3. As etapas feitas em Excel são identificadas e não são recriadas aqui.
# 4. As saídas são gravadas em dir_saida sem chamadas interativas.
# ==============================================================================


options(stringsAsFactors = FALSE, survey.lonely.psu = "adjust")


# CONFIGURACAO ---------------------------------------------------------------
dir_sih_raw <- "dados/sih_raw"
arquivo_renda_pnadc <- "dados/base_pnadc_regiao.xlsx"
dir_saida <- "resultados/servicos_medicos"
dir.create(dir_sih_raw, recursive = TRUE, showWarnings = FALSE)
dir.create(dir_saida, recursive = TRUE, showWarnings = FALSE)


pacotes <- c("writexl","microdatasus","dplyr","survey","purrr","ggplot2",
             "scales","arrow","readxl","tidyr","stringr")
faltantes <- pacotes[!vapply(pacotes, requireNamespace, logical(1), quietly = TRUE)]
if (length(faltantes)) stop("Instale os pacotes: ", paste(faltantes, collapse = ", "))










# ============================================================
# Baixar dados de agressões para todo o período 2008:2025
# ============================================================


# 1. Definir período de interese


anos = 2008:2025


# 2. Criar pasta principal para salvar bases mensais


dir.create(dir_sih_raw,showWarnings = FALSE)


# 3. Criar tabela para registrar erros


erros = data.frame(ano = integer(), mes = integer())


# 4. Loop por ano


for (ano in anos) {
  
  cat("\n=============================\n")
  cat("Iniciando ano:", ano, "\n")
  cat("=============================\n")
  
  # Criar pasta do ano
  
  pasta_ano <- paste0(
    "SIH_RAW/SIH_",
    ano)
  
  dir.create(
    pasta_ano,
    showWarnings = FALSE)
  
  # ============================================================
  # Loop por mês
  # ============================================================
  
  for (mes in 1:12) {
    
    arquivo_saida <- paste0(
      pasta_ano,
      "/SIH_",
      ano,
      "_",
      sprintf("%02d", mes),
      ".parquet")
    
    # ---------------------------------------------------------
    # Checkpoint:
    # se já existe, pula
    # ---------------------------------------------------------
    
    if(file.exists(arquivo_saida)){
      cat(
        "Já existe:",
        ano,
        "-",
        sprintf("%02d", mes),
        "\n")
      next}
    
    cat(
      "\nBaixando:",
      ano,
      "-",
      sprintf("%02d", mes),
      "\n")
    
    # ---------------------------------------------------------
    # Download mês específico
    # ---------------------------------------------------------
    
    dados <- tryCatch(
      
      
      fetch_datasus(
        
        year_start = ano,
        month_start = mes,
        
        year_end = ano,
        month_end = mes,
        
        uf = "all",
        
        information_system = "SIH-RD"
        
      ),
      
      
      error = function(e){
        
        
        cat(
          "ERRO no ano:",
          ano,
          "mês:",
          mes,
          "\n"
        )
        
        
        cat(
          e$message,
          "\n"
        )
        
        
        erros <<- rbind(
          erros,
          data.frame(
            ano = ano,
            mes = mes
          )
        )
        
        
        return(NULL)
        
      }
      
    )
    
    
    
    # ---------------------------------------------------------
    # Se deu erro, pula para próximo mês
    # ---------------------------------------------------------
    
    if(is.null(dados)){
      
      next
      
    }
    
    
    
    # ---------------------------------------------------------
    # Salvar parquet
    # ---------------------------------------------------------
    
    
    write_parquet(
      dados,
      arquivo_saida
    )
    
    
    
    cat(
      "Salvo:",
      arquivo_saida,
      "\n"
    )
    
    
    
    # ---------------------------------------------------------
    # Limpar memória
    # ---------------------------------------------------------
    
    
    rm(dados)
    
    
    gc()
    
    
    
  }
  
  
}




# 5. Salvar log final de erros


write.csv(erros, "SIH_RAW/erros_download.csv", row.names = FALSE)


cat("\n=============================\n")
cat("Download finalizado\n")
cat("=============================\n")






#####################################################################
#####################################################################
#####################################################################


          # ETAPA DE VALIDAÇÃO (Teste para 01/2024) # 


#####################################################################
#####################################################################
#####################################################################




# 1. Carregar base teste (Janeiro 2024)


teste = read_parquet(
  "SIH_RAW/SIH_2024/SIH_2024_01.parquet")




# 2. Função para identificar códigos de agressão
#    Baseada no apêndice metodológico:
#    X85-X99
#    W34
#    Y00-Y09
#    Y24


eh_agressao = function(x){
  
  cid = substr(x,1,3)
  
  (
    cid >= "X85" & cid <= "X99"
  ) |
    (
      cid >= "Y00" & cid <= "Y09"
    ) |
    cid == "W34" |
    cid == "Y24"
  
}


# 3. Identificar internações por agressão


agressoes = teste %>%
  
  filter(
    
    eh_agressao(DIAGSEC1) |
      eh_agressao(DIAGSEC2) |
      eh_agressao(DIAGSEC3) |
      eh_agressao(DIAGSEC4) |
      eh_agressao(DIAGSEC5) |
      eh_agressao(DIAGSEC6) |
      eh_agressao(DIAGSEC7) |
      eh_agressao(DIAGSEC8) |
      eh_agressao(DIAGSEC9))




# 4. Conferir número de internações


nrow(agressoes)


# 5. Conferir distribuição dos CIDs encontrados


agressoes %>%
  
  select(starts_with("DIAGSEC")) %>%
  
  pivot_longer(
    everything(),
    values_to = "CID"
  ) %>%
  
  filter(
    eh_agressao(CID)
  ) %>%
  
  count(CID, sort = TRUE)




# 6. Indicadores principais - Janeiro 2024


resultado_jan2024 = agressoes %>%
  
  summarise(
    
    internacoes_agressao = n(),
    
    
    custo_SUS = sum(
      VAL_TOT,
      na.rm = TRUE
    ),
    
    
    custo_medio_internacao = mean(
      VAL_TOT,
      na.rm = TRUE
    ),
    
    
    dias_totais_internacao = sum(
      DIAS_PERM,
      na.rm = TRUE
    ),
    
    
    dias_medios_internacao = mean(
      DIAS_PERM,
      na.rm = TRUE
    ),
    
    
    obitos_hospitalares = sum(
      MORTE == 1,
      na.rm = TRUE
    )
    
  )




resultado_jan2024


# 7. Internações não fatais
# (base para perda produtiva temporária)


agressoes_recuperacao = agressoes %>%
  
  filter(
    MORTE != 1)


resultado_recuperacao = agressoes_recuperacao %>%
  
  summarise(internacoes_nao_fatais = n(),
            
            
            dias_recuperacao = sum(
              DIAS_PERM,
              na.rm = TRUE))




resultado_recuperacao




# 8. Estatísticas da idade das vítimas


summary(
  agressoes$IDADE)




idade_media_agressoes =
  agressoes %>%
  
  summarise(
    
    idade_media =
      weighted.mean(IDADE, VAL_TOT, na.rm = TRUE))




idade_media_agressoes




# 9. Conferência dos valores SUS


summary(
  agressoes$VAL_TOT)








#####################################################################
#####################################################################
#####################################################################


                # FIM DA ETAPA DE VALIDAÇÃO # 


#####################################################################
#####################################################################
#####################################################################






# ==================================================================
# ETAPA A: obter dados do Sistema de Informações Hospitalares (SIH)
# ==================================================================


# 1. Criar variável de identificação da região da agressão 


agressoes =
  agressoes %>%
  mutate(UF = substr(UF_ZI,1,2))


agressoes =
  agressoes %>%
  
  mutate(
    
    regiao =
      case_when(
        
        UF %in% c(
          "11","12","13","14","15","16","17"
        )
        ~ "Norte",
        
        
        UF %in% c(
          "21","22","23","24","25","26","27","28","29"
        )
        ~ "Nordeste",
        
        
        UF %in% c(
          "31","32","33","35"
        )
        ~ "Sudeste",
        
        
        UF %in% c(
          "41","42","43"
        )
        ~ "Sul",
        
        
        UF %in% c(
          "50","51","52","53"
        )
        ~ "Centro-Oeste"
        
      )
    
  )




# 2. Agrupar =< de 14 anos e => 70 em grupos 


agressoes_produtividade = agressoes %>%
  
  filter(
    MORTE != 1) %>%
  
  mutate(
    
    idade_ajustada =
      case_when(
        
        IDADE <= 14 ~ 14,
        
        IDADE >= 70 ~ 70,
        
        TRUE ~ IDADE))




# 3. Juntar bases (internações por agressão + perdas produtivas)


renda_pnadc <- readxl::read_excel(arquivo_renda_pnadc)


agressoes_produtividade = agressoes_produtividade %>%
  left_join(renda_pnadc,
    by = c(
      "idade_ajustada" = "idade", "regiao" = "regiao"))


# 4. Transformar renda mensal (renda_esperada) em renda diária
# Calcular a perda produtiva individual (renda_diaria * DIAS_PERM)


agressoes_produtividade = agressoes_produtividade %>%
  mutate(renda_diaria = renda_esperada / 30,
    perda_produtiva_individual = renda_diaria * DIAS_PERM)




# 5. Função para processar arquivos mensais da pasta dir_sih_raw


eh_agressao = function(x){
  
  cid = substr(x,1,3)
  
  (
    cid >= "X85" & cid <= "X99"
  ) |
    
    (
      cid >= "Y00" & cid <= "Y09"
    ) |
    
    cid == "W34" |
    
    cid == "Y24"
  
}


processar_mes = function(arquivo){
  
  cat(
    "\nProcessando:",
    arquivo,
    "\n"
  )
  
  # ----------------------------------------------------------
  # Ler arquivo
  # ----------------------------------------------------------
  
  dados =
    arrow::read_parquet(
      arquivo
    )
  
  
  
  # ----------------------------------------------------------
  # Identificar colunas de diagnóstico disponíveis
  # Compatível com 2008-2025
  # ----------------------------------------------------------
  
  colunas_diag =
    names(dados)[
      grepl(
        "^DIAG",
        names(dados)
      )
    ]
  
  
  
  # ----------------------------------------------------------
  # Filtrar agressões
  # ----------------------------------------------------------
  
  agressoes =
    dados %>%
    
    filter(
      
      if_any(
        all_of(colunas_diag),
        eh_agressao
      )
      
    )
  
  
  
  # ----------------------------------------------------------
  # Criar região
  # ----------------------------------------------------------
  
  agressoes =
    agressoes %>%
    
    mutate(
      
      UF =
        substr(
          UF_ZI,
          1,
          2
        )
      
    ) %>%
    
    mutate(
      
      regiao =
        case_when(
          
          UF %in% c(
            "11","12","13","14","15","16","17"
          )
          ~ "Norte",
          
          UF %in% c(
            "21","22","23","24","25","26","27","28","29"
          )
          ~ "Nordeste",
          
          UF %in% c(
            "31","32","33","35"
          )
          ~ "Sudeste",
          
          UF %in% c(
            "41","42","43"
          )
          ~ "Sul",
          
          UF %in% c(
            "50","51","52","53"
          )
          ~ "Centro-Oeste"
          
        )
      
    )
  
  
  
  # ----------------------------------------------------------
  # Não fatais
  # ----------------------------------------------------------
  
  agressoes_produtividade =
    agressoes %>%
    
    filter(
      MORTE != 1
    ) %>%
    
    mutate(
      
      idade_ajustada =
        case_when(
          
          IDADE <= 14 ~ 14,
          
          IDADE >= 70 ~ 70,
          
          TRUE ~ IDADE
          
        )
      
    )
  
  
  
  # ----------------------------------------------------------
  # Join PNADC
  # ----------------------------------------------------------
  
  agressoes_produtividade =
    agressoes_produtividade %>%
    
    left_join(
      
      renda_pnadc,
      
      by = c(
        "idade_ajustada" = "idade",
        "regiao" = "regiao"
      )
      
    )
  
  
  
  # ----------------------------------------------------------
  # Renda diária
  # ----------------------------------------------------------
  
  agressoes_produtividade =
    agressoes_produtividade %>%
    
    mutate(
      
      renda_diaria =
        renda_esperada / 30,
      
      perda_produtiva_individual =
        renda_diaria * DIAS_PERM
      
    )
  
  
  
  # ----------------------------------------------------------
  # Agregação final
  # ----------------------------------------------------------
  
  resultado =
    agressoes_produtividade %>%
    
    summarise(
      
      ano =
        first(
          as.numeric(ANO_CMPT)
        ),
      
      mes =
        first(
          as.numeric(MES_CMPT)
        ),
      
      internacoes_nao_fatais =
        n(),
      
      renda_esperada_media =
        mean(
          renda_esperada,
          na.rm = TRUE
        ),
      
      perda_produtiva_temporaria =
        sum(
          perda_produtiva_individual,
          na.rm = TRUE
        )
      
    )
  
  
  
  resultado_hospitalar =
    agressoes %>%
    
    summarise(
      
      internacoes_agressao =
        n(),
      
      obitos_hospitalares =
        sum(
          MORTE == 1,
          na.rm = TRUE
        ),
      
      custo_SUS =
        sum(
          VAL_TOT,
          na.rm = TRUE
        ),
      
      dias_totais_internacao =
        sum(
          DIAS_PERM,
          na.rm = TRUE
        ),
      
      dias_medios_internacao =
        mean(
          DIAS_PERM,
          na.rm = TRUE
        ),
      
      idade_media_internados =
        mean(
          IDADE,
          na.rm = TRUE
        )
      
    )
  
  
  
  bind_cols(
    
    resultado,
    
    resultado_hospitalar
    
  ) %>%
    
    mutate(
      
      custo_medico_total =
        custo_SUS +
        perda_produtiva_temporaria
      
    )
  
}


# 6. Rodar para toda a série


arquivos =
  list.files(
    
    dir_sih_raw,
    
    pattern = "\\.parquet$",
    
    recursive = TRUE,
    
    full.names = TRUE
    
  )


length(arquivos)




# 7. Processar todos os dados referentes a todos os meses (2008:2025)


resultado_final =
  purrr::map_dfr(
    
    arquivos,
    
    ~ tryCatch(
      
      processar_mes(.x),
      
      error = function(e){
        
        cat(
          "\n=================================\n"
        )
        
        cat(
          "ERRO NO ARQUIVO:\n",
          .x,
          "\n"
        )
        
        cat(
          "MENSAGEM:\n",
          e$message,
          "\n"
        )
        
        cat(
          "=================================\n"
        )
        
        return(NULL)
        
      }
      
    )
    
  )




# 7.5. Imputar setembro de 2009 ausente


# verificar se realmente está faltando
resultado_final %>%
  filter(ano == 2009, mes == 9)


# criar linha imputada usando média dos demais setembros


setembro_2009 =
  resultado_final %>%
  
  filter(
    mes == 9,
    ano != 2009
  ) %>%
  
  summarise(
    
    across(
      where(is.numeric),
      mean,
      na.rm = TRUE
    )
    
  ) %>%
  
  mutate(
    
    ano = 2009,
    mes = 9
    
  ) %>%
  
  select(names(resultado_final))


# adicionar linha


resultado_final =
  bind_rows(
    resultado_final,
    setembro_2009
  ) %>%
  
  arrange(
    ano,
    mes
  )


nrow(resultado_final)




# 8. Checagem dos resultados


resultado_final %>%
  
  summarise(
    
    custo_SUS_total =
      sum(
        custo_SUS,
        na.rm = TRUE
      ),
    
    perda_produtiva_total =
      sum(
        perda_produtiva_temporaria,
        na.rm = TRUE
      ),
    
    custo_total =
      sum(
        custo_medico_total,
        na.rm = TRUE
      )
    
  )


# 9. Agregar resultados para nível anual


resultado_anual =
  resultado_final %>%
  
  group_by(ano) %>%
  
  summarise(
    
    internacoes_agressao =
      sum(internacoes_agressao),
    
    internacoes_nao_fatais =
      sum(internacoes_nao_fatais),
    
    obitos_hospitalares =
      sum(obitos_hospitalares),
    
    dias_totais_internacao =
      sum(dias_totais_internacao),
    
    custo_SUS =
      sum(custo_SUS),
    
    perda_produtiva_temporaria =
      sum(perda_produtiva_temporaria),
    
    custo_medico_total =
      sum(custo_medico_total),
    
    .groups = "drop"
    
  )


# 10. Salvar resultados


write_xlsx(
  resultado_final,
  file.path(dir_saida, "custos_medicos_mensais_2008_2025.xlsx"))


write_xlsx(
  resultado_anual,
  file.path(dir_saida, "custos_medicos_anuais_2008_2025.xlsx"))