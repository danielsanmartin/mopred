🚀 Iniciando análise de modelos temporais para detecção de clonagem
======================================================================
🚀 INICIANDO TESTE DE MODELOS TEMPORAIS
============================================================
✅ Configuração carregada de configs/config.json
🎬 Simulador Streaming ALPR inicializado
📋 Configurações principais:
   ⏱️  Tempo de simulação: 6h
   📡 Total de sensores: 200
   🏙️  Cidades: 20
   📊 Passagens por veículo: 2-2
🎬 Iniciando simulação streaming ALPR completa
============================================================
✅ 100,000 veículos carregados de csvs/veiculos_gerados_com_clones.csv
   🚗 Veículos normais: 96,000
   ⚠️  Veículos clonados: 4,000
📡 Distribuindo 200 sensores...
✅ 200 sensores distribuídos
🎬 Gerando eventos cronológicos para 100,000 veículos...
✅ 200,000 eventos gerados e ordenados cronologicamente
   📅 Período: 2025-08-01 03:00 até 2025-08-01 08:59
   ⏱️ Duração: 6.0 horas
   📊 Taxa média: 33333.7 eventos/hora
📁 Arquivo salvo: csvs\passagens_streaming.csv
📊 Estatísticas dos eventos:
   🚗 Total de eventos: 200,000
   🏷️ Placas distintas: 98,000
   📡 Câmeras utilizadas: 200
   ⚠️ Eventos de veículos clonados: 8,000
============================================================
🎉 Simulação concluída! Eventos prontos para streaming.

🔒 APLICANDO PSEUDONIMIZAÇÃO...
🔒 Aplicando pseudonimização nas placas...
✅ 98000 placas únicas pseudonimizadas
📊 Total de eventos processados: 200000
🔄 Simulando mudanças temporais nos dados...
  📍 Criando zonas quentes baseadas na configuração...
  ✅ 26401 eventos marcados como clonados nas zonas quentes
✅ Fases criadas:
  Fase 1: 66,666 eventos (baseline)
  Fase 2: 66,666 eventos (+ clonagem)
  Fase 3: 66,668 eventos (novos padrões)

🌱 PREPARANDO TREINO INICIAL...
⚠️ SMOTE desabilitado pela configuração.
✅ Dados de treino preparados (sem balanceamento):
   📊 27,647 pares de eventos
   Classe 0: 25854 exemplos
   Classe 1: 1793 exemplos
   🧬 Média de semelhança: 0.991

🔎 Shape X_treino: (27647, 3), Shape X_treino_multimodal: (27647, 7), Shape y_treino: (27647,)

🌟 Treinando modelo tradicional (apenas features básicas)...
🌳 Treinando Random Forest Tradicional...
✅ Modelo tradicional treinado com 27,647 amostras

🌟 Treinando modelo tradicional (multimodal: infrações + semelhança)...
🌳 Treinando Random Forest Tradicional (multimodal: infrações + semelhança visual)... 
✅ Modelo tradicional multimodal treinado com 27,647 amostras

🕒 TESTANDO EM JANELAS TEMPORAIS...

==================== FASE 1 ====================

📊 Avaliando Janela 1 (22222 eventos) [básico]

📊 Avaliando Janela 1 (22222 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 1
📊 Calculando explicabilidade SHAP para 5897 pares...
✅ 579 alertas únicos salvos em: alertas_gerados\alertas_janela_001.ndjson
📊 1 alertas duplicados removidos
🚨 Janela 1: 579 alertas gerados

📊 Avaliando Janela 2 (22222 eventos) [básico]

📊 Avaliando Janela 2 (22222 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 2
📊 Calculando explicabilidade SHAP para 2988 pares...
✅ 426 alertas únicos salvos em: alertas_gerados\alertas_janela_002.ndjson
📊 1 alertas duplicados removidos
🚨 Janela 2: 426 alertas gerados

📊 Avaliando Janela 3 (22222 eventos) [básico]

📊 Avaliando Janela 3 (22222 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 3
📊 Calculando explicabilidade SHAP para 2798 pares...
✅ 408 alertas únicos salvos em: alertas_gerados\alertas_janela_003.ndjson
📊 2 alertas duplicados removidos
🚨 Janela 3: 408 alertas gerados

==================== FASE 2 ====================

📊 Avaliando Janela 4 (22222 eventos) [básico]

📊 Avaliando Janela 4 (22222 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 4
📊 Calculando explicabilidade SHAP para 2682 pares...
✅ 395 alertas únicos salvos em: alertas_gerados\alertas_janela_004.ndjson
📊 2 alertas duplicados removidos
🚨 Janela 4: 395 alertas gerados

📊 Avaliando Janela 5 (22222 eventos) [básico]

📊 Avaliando Janela 5 (22222 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 5
📊 Calculando explicabilidade SHAP para 2639 pares...
✅ 377 alertas únicos salvos em: alertas_gerados\alertas_janela_005.ndjson
📊 4 alertas duplicados removidos
🚨 Janela 5: 377 alertas gerados

📊 Avaliando Janela 6 (22222 eventos) [básico]

📊 Avaliando Janela 6 (22222 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 6
📊 Calculando explicabilidade SHAP para 2686 pares...
✅ 371 alertas únicos salvos em: alertas_gerados\alertas_janela_006.ndjson
📊 1 alertas duplicados removidos
🚨 Janela 6: 371 alertas gerados

==================== FASE 3 ====================

📊 Avaliando Janela 7 (22222 eventos) [básico]

📊 Avaliando Janela 7 (22222 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 7
📊 Calculando explicabilidade SHAP para 2706 pares...
✅ 354 alertas únicos salvos em: alertas_gerados\alertas_janela_007.ndjson
📊 2 alertas duplicados removidos
🚨 Janela 7: 354 alertas gerados

📊 Avaliando Janela 8 (22222 eventos) [básico]

📊 Avaliando Janela 8 (22222 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 8
📊 Calculando explicabilidade SHAP para 2751 pares...
✅ 406 alertas únicos salvos em: alertas_gerados\alertas_janela_008.ndjson
📊 1 alertas duplicados removidos
🚨 Janela 8: 406 alertas gerados

📊 Avaliando Janela 9 (22224 eventos) [básico]

📊 Avaliando Janela 9 (22224 eventos) [multimodal]

🚨 GERAÇÃO DE ALERTAS - JANELA 9
📊 Calculando explicabilidade SHAP para 5139 pares...
✅ 191 alertas únicos salvos em: alertas_gerados\alertas_janela_009.ndjson
📊 1 alertas duplicados removidos
🚨 Janela 9: 191 alertas gerados

📈 RELATÓRIO FINAL - COMPARAÇÃO DE MODELOS
============================================================

📊 MÉDIAS GERAIS:
Random Forest Tradicional:
  Accuracy:  0.818 ± 0.150
  Precision: 1.000 ± 0.000
  Recall:    0.528 ± 0.326
  F1-Score:  0.638 ± 0.282

Random Forest Adaptativo:
  Accuracy:  0.826 ± 0.115
  Precision: 0.833 ± 0.324
  Recall:    0.496 ± 0.289
  F1-Score:  0.605 ± 0.284

📈 TENDÊNCIAS AO LONGO DO TEMPO:
F1-Score por Janela:
  Janela 1: Trad=0.957 | Adapt=0.000 🏛️
  Janela 2: Trad=0.969 | Adapt=0.966 🏛️
  Janela 3: Trad=0.977 | Adapt=0.967 🏛️
  Janela 4: Trad=0.622 | Adapt=0.619 🏛️
  Janela 5: Trad=0.600 | Adapt=0.618 🔄
  Janela 6: Trad=0.574 | Adapt=0.588 🔄
  Janela 7: Trad=0.426 | Adapt=0.634 🔄
  Janela 8: Trad=0.459 | Adapt=0.564 🔄
  Janela 9: Trad=0.160 | Adapt=0.489 🔄

🏆 RESULTADO FINAL:
  Vitórias Tradicional: 4
  Vitórias Adaptativo: 5
  Empates: 0
  🏆 VENCEDOR: Random Forest Adaptativo

💾 Resultados salvos em: csvs\comparacao_modelos_resultados.csv (cenários básico e multimodal)

🚨 CONSOLIDAÇÃO DE ALERTAS GERADOS...
✅ 3507 alertas consolidados em: alertas_gerados\alertas_consolidados.ndjson
📊 Arquivos de janela: 9 arquivos
📁 Pasta de alertas: alertas_gerados

🔎 EXPLICABILIDADE (XAI) PARA RANDOM FOREST TRADICIONAL MULTIMODAL:
Importância global das features:
  dist_km: 0.358
  delta_t_segundos: 0.209
  velocidade_kmh: 0.251
  num_infracoes: 0.112
  marca_modelo_igual: 0.045
  tipo_igual: 0.011
  cor_igual: 0.014

🚨 GERAÇÃO DE ALERTAS JSON-LD...
✅ 1135 alertas gerados para casos suspeitos (score >= 0.8)
📁 Alertas salvos em: alertas_gerados\alertas_gerados.ndjson

Exemplo de explicação SHAP para os primeiros casos clonados (formato amigável):       
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|

Caso 1 - Predição: CLONADO - Escore de suspeição: 100.00%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |     262.570|       0.240|🔴 + Alto impacto      |
|Tempo entre leituras (segundos)       |     105.000|       0.110|🔴 + Alto impacto      |
|Velocidade estimada (km/h)            |    9002.413|       0.183|🔴 + Alto impacto      |
|Número de infrações                   |       3.000|      -0.020|🟡 - Impacto moderado  |
|Marca/modelo iguais                   |       1.000|      -0.008|🟡 - Impacto moderado  |
|Tipo igual                            |       1.000|      -0.002|🟢 - Baixo impacto     |
|Cor igual                             |       1.000|      -0.003|🟢 - Baixo impacto     |
Resumo: Distância entre câmeras (km) teve forte influência na decisão. Tempo entre leituras (segundos) teve forte influência na decisão. Velocidade estimada (km/h) teve forte influência na decisão. O número de infrações teve impacto moderado na decisão. A similaridade de marca/modelo iguais teve impacto moderado na decisão.

Caso 2 - Predição: CLONADO - Escore de suspeição: 100.00%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |     265.692|       0.156|🔴 + Alto impacto      |
|Tempo entre leituras (segundos)       |    2929.941|      -0.043|🟡 - Impacto moderado  |
|Velocidade estimada (km/h)            |     326.453|       0.112|🔴 + Alto impacto      |
|Número de infrações                   |       3.000|      -0.015|🟢 - Baixo impacto     |
|Marca/modelo iguais                   |       0.000|       0.202|🔴 + Alto impacto      |
|Tipo igual                            |       1.000|      -0.002|🟢 - Baixo impacto     |
|Cor igual                             |       0.000|       0.091|🟡 + Impacto moderado  |
Resumo: Distância entre câmeras (km) teve forte influência na decisão. Velocidade estimada (km/h) teve forte influência na decisão. A similaridade de marca/modelo iguais teve forte influência na decisão de clonagem. A similaridade de cor igual teve impacto moderado na decisão.

Caso 3 - Predição: CLONADO - Escore de suspeição: 97.49%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |       3.141|       0.009|🟡 + Impacto moderado  |
|Tempo entre leituras (segundos)       |     586.000|       0.019|🔴 + Alto impacto      |
|Velocidade estimada (km/h)            |      19.297|      -0.090|🔴 - Alto impacto      |
|Número de infrações                   |      18.000|       0.559|🔴 + Alto impacto      |
|Marca/modelo iguais                   |       1.000|      -0.012|🟡 - Impacto moderado  |
|Tipo igual                            |       1.000|      -0.005|🟢 - Baixo impacto     |
|Cor igual                             |       1.000|      -0.005|🟢 - Baixo impacto     |
Resumo: Tempo entre leituras (segundos) teve forte influência na decisão. Velocidade estimada (km/h) teve forte influência na decisão. O número de infrações teve forte influência na decisão de clonagem. A similaridade de marca/modelo iguais teve impacto moderado na decisão.

Caso 32 - Predição: CLONADO - Escore de suspeição: 100.00%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |     271.020|       0.237|🔴 + Alto impacto      |
|Tempo entre leituras (segundos)       |     138.000|       0.107|🔴 + Alto impacto      |
|Velocidade estimada (km/h)            |    7070.084|       0.187|🔴 + Alto impacto      |
|Número de infrações                   |       1.000|      -0.018|🟡 - Impacto moderado  |
|Marca/modelo iguais                   |       1.000|      -0.008|🟡 - Impacto moderado  |
|Tipo igual                            |       1.000|      -0.002|🟢 - Baixo impacto     |
|Cor igual                             |       1.000|      -0.003|🟢 - Baixo impacto     |
Resumo: Distância entre câmeras (km) teve forte influência na decisão. Tempo entre leituras (segundos) teve forte influência na decisão. Velocidade estimada (km/h) teve forte influência na decisão. O número de infrações teve impacto moderado na decisão. A similaridade de marca/modelo iguais teve impacto moderado na decisão.

Caso 33 - Predição: CLONADO - Escore de suspeição: 100.00%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |     152.233|       0.119|🔴 + Alto impacto      |
|Tempo entre leituras (segundos)       |    1958.057|      -0.038|🟢 - Baixo impacto     |
|Velocidade estimada (km/h)            |     279.890|       0.079|🟡 + Impacto moderado  |
|Número de infrações                   |       2.000|      -0.015|🟢 - Baixo impacto     |
|Marca/modelo iguais                   |       0.000|       0.191|🔴 + Alto impacto      |
|Tipo igual                            |       0.000|       0.084|🔴 + Alto impacto      |
|Cor igual                             |       0.000|       0.080|🟡 + Impacto moderado  |
Resumo: Distância entre câmeras (km) teve forte influência na decisão. A similaridade de marca/modelo iguais teve forte influência na decisão de clonagem. A similaridade de tipo igual teve forte influência na decisão de clonagem. A similaridade de cor igual teve impacto moderado na decisão.

🪟 TESTE ADICIONAL COM STREAMING POR JANELAS...
🔄 Reinicializando modelo adaptativo para teste limpo...
🪟 Iniciando modo: JANELAS TEMPORAIS (2.0h por janela)
📊 Janela 1: 68,103 eventos (03:00:00 - 05:00:00)

--- Janela Streaming 1 ---

📊 Avaliando Janela Stream-1 (68103 eventos) [básico]
📊 Janela 2: 79,750 eventos (05:00:00 - 07:00:00)

--- Janela Streaming 2 ---
🔄 Treinando modelo adaptativo com janela anterior...

📊 Avaliando Janela Stream-2 (79750 eventos) [básico]
📊 Janela 3: 52,147 eventos (07:00:00 - 08:59:59)

--- Janela Streaming 3 ---
🔄 Treinando modelo adaptativo com janela anterior...

📊 Avaliando Janela Stream-3 (52147 eventos) [básico]
✅ Teste de streaming concluído com 3 janelas processadas
🪟 Iniciando modo: JANELAS TEMPORAIS (2.0h por janela)
📊 Janela 1: 68,103 eventos (03:00:00 - 05:00:00)
📊 Janela 2: 79,750 eventos (05:00:00 - 07:00:00)
📊 Janela 3: 52,147 eventos (07:00:00 - 08:59:59)

🔎 EXPLICABILIDADE (XAI) PARA CASOS CLONADOS DO STREAMING (MULTIMODAL):
Importância global das features:
  dist_km: 0.358
  delta_t_segundos: 0.209
  velocidade_kmh: 0.251
  num_infracoes: 0.112
  marca_modelo_igual: 0.045
  tipo_igual: 0.011
  cor_igual: 0.014

ℹ️ Geração de alertas desabilitada na configuração

Exemplo de explicação SHAP para os primeiros casos clonados (formato amigável):       
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|

Caso 8 - Predição: CLONADO - Escore de suspeição: 100.00%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |     152.233|       0.124|🔴 + Alto impacto      |
|Tempo entre leituras (segundos)       |     239.000|       0.089|🟡 + Impacto moderado  |
|Velocidade estimada (km/h)            |    2293.056|       0.125|🔴 + Alto impacto      |
|Número de infrações                   |      18.000|       0.174|🔴 + Alto impacto      |
|Marca/modelo iguais                   |       1.000|      -0.007|🟡 - Impacto moderado  |
|Tipo igual                            |       1.000|      -0.002|🟢 - Baixo impacto     |
|Cor igual                             |       1.000|      -0.002|🟢 - Baixo impacto     |
Resumo: Distância entre câmeras (km) teve forte influência na decisão. Velocidade estimada (km/h) teve forte influência na decisão. O número de infrações teve forte influência na decisão de clonagem. A similaridade de marca/modelo iguais teve impacto moderado na decisão.

Caso 9 - Predição: CLONADO - Escore de suspeição: 100.00%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |     271.020|       0.239|🔴 + Alto impacto      |
|Tempo entre leituras (segundos)       |     297.000|       0.110|🔴 + Alto impacto      |
|Velocidade estimada (km/h)            |    3285.089|       0.184|🔴 + Alto impacto      |
|Número de infrações                   |       2.000|      -0.019|🟡 - Impacto moderado  |
|Marca/modelo iguais                   |       1.000|      -0.008|🟡 - Impacto moderado  |
|Tipo igual                            |       1.000|      -0.002|🟢 - Baixo impacto     |
|Cor igual                             |       1.000|      -0.003|🟢 - Baixo impacto     |
Resumo: Distância entre câmeras (km) teve forte influência na decisão. Tempo entre leituras (segundos) teve forte influência na decisão. Velocidade estimada (km/h) teve forte influência na decisão. O número de infrações teve impacto moderado na decisão. A similaridade de marca/modelo iguais teve impacto moderado na decisão.

Caso 12 - Predição: CLONADO - Escore de suspeição: 100.00%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |     267.902|       0.133|🔴 + Alto impacto      |
|Tempo entre leituras (segundos)       |     157.000|       0.080|🟡 + Impacto moderado  |
|Velocidade estimada (km/h)            |    6142.968|       0.125|🔴 + Alto impacto      |
   |
|Tipo igual                            |       0.000|       0.071|🟡 + Impacto moderado  |
|Cor igual                             |       0.000|       0.071|🟡 + Impacto moderado  |
Resumo: Distância entre câmeras (km) teve forte influência na decisão. O número de infrações teve forte influência na decisão de clonagem. A similaridade de marca/modelo iguais teve forte influência na decisão de clonagem. A similaridade de tipo igual teve impacto moderado na decisão. A similaridade de cor igual teve impacto moderado na decisão.

Caso 14 - Predição: CLONADO - Escore de suspeição: 100.00%
|            Característica            |   Valor    |Impacto SHAP|    Interpretação     |
|--------------------------------------|------------|------------|----------------------|
|Distância entre câmeras (km)          |     402.843|       0.240|🔴 + Alto impacto      |
|Tempo entre leituras (segundos)       |     215.000|       0.102|🔴 + Alto impacto      |
|Velocidade estimada (km/h)            |    6745.272|       0.188|🔴 + Alto impacto      |
|Número de infrações                   |       0.000|      -0.018|🟡 - Impacto moderado  |
|Marca/modelo iguais                   |       1.000|      -0.007|🟡 - Impacto moderado  |
|Tipo igual                            |       1.000|      -0.002|🟢 - Baixo impacto     |
|Cor igual                             |       1.000|      -0.002|🟢 - Baixo impacto     |
Resumo: Distância entre câmeras (km) teve forte influência na decisão. Tempo entre leituras (segundos) teve forte influência na decisão. Velocidade estimada (km/h) teve forte influência na decisão. O número de infrações teve impacto moderado na decisão. A similaridade de marca/modelo iguais teve impacto moderado na decisão.