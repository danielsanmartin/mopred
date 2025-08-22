# MOPRED - Sistema de Detecção de Clonagem Veicular


> Versão 2.2.0 • Última atualização: 2025-08-22

---

## 1. Visão Geral

O MOPRED é um sistema completo para detecção de clonagem veicular que combina:
* Simulação realística de passagens ALPR
* Aprendizado adaptativo (concept drift / evolução temporal)
* Features multimodais (contexto físico + semântico + comportamento)
* Explicabilidade integrada (SHAP contextual) nos alertas
* Pseudonimização forte para privacidade
* Geração de alertas padronizados em JSON-LD
* Processamento temporal em micro-batches (near-real-time)

### Objetivos Principais
1. Comparar modelos tradicionais vs. adaptativos
2. Avaliar impacto de features multimodais (3 vs 7 dimensões)
3. Integrar explicabilidade XAI operacional (SHAP + interpretação dinâmica)
4. Simular mudanças temporais e drifts comportamentais
5. Preservar privacidade via pseudonimização irreversível (HMAC-SHA256)
6. Gerar alertas semânticos interoperáveis (JSON-LD)
7. Sustentar pesquisa acadêmica em detecção adaptativa de clonagem

### Hipóteses de Pesquisa
* Modelos adaptativos convergem mais rápido após drift (< 3 janelas)
* Features multimodais elevam F1 em relação ao conjunto básico
* Explicabilidade evidencia padrão diferenciado de clones (distância/tempo + semelhança + infrações)
* Pseudonimização mantém utilidade analítica sem comprometer privacidade

---

## 2. Arquitetura Geral

| Camada | Função | Arquivo(s) |
|--------|--------|------------|
| Simulação | Geração de passagens e micro-batches | `simulador_streaming_alpr.py` |
| Geração de Dados | Veículos e clones sintéticos | `gerador_veiculos.py` |
| Feature Engineering | Extração 3D e 7D + contexto | `utils.py` |
| Modelagem | Random Forest (estática) + Adaptive Random Forest | `comparador_modelos.py` |
| Explicabilidade | SHAP + interpretação dinâmica | `alertas.py`, `validacao_modelo_conceitual.py` |
| Alertas | JSON-LD + deduplicação + classificação | `alertas.py` |
| Orquestração Experimental | Pipeline temporal completo | `validacao_modelo_conceitual.py` |

### Features
```python
# Básico (3):
[distancia_km, tempo_segundos, velocidade_kmh]

# Multimodal (7):
[distancia_km, tempo_segundos, velocidade_kmh,
 num_infracoes, marca_modelo_igual, tipo_igual, cor_igual]
```

### Modelo Adaptativo
Adaptive Random Forest (aprendizado incremental por janela) preserva histórico enquanto incorpora novos padrões, mitigando perda de desempenho pós-drift.

### Processamento Temporal
Estrutura de micro-batches: cada janela = ciclo completo (atualização adaptativa + avaliação + geração de alertas elegíveis).

---

## 3. Fluxo de Execução
1. Geração / carga de dados sintéticos
2. Pré-processamento + pseudonimização (opcional)
3. Extração de pares e features iniciais
4. Treino inicial dos modelos tradicionais (3D e 7D)
5. Loop temporal (janelas):
   * Atualização incremental do modelo adaptativo
   * Inferência e métricas (Accuracy, Precision, Recall, F1)
   * Análise de drift implícita (variação métrica entre janelas)
   * Geração de alertas JSON-LD (score >= limiar)
6. Consolidação + relatórios + explicabilidade final

---

## 4. Funcionalidades Avançadas

### Pseudonimização (HMAC-SHA256)
Mantém consistência longitudinal sem expor placas reais.

### Balanceamento (SMOTE Adaptativo)
Aplicado condicionalmente conforme configuração e tamanho mínimo de minoria.

### Explicabilidade Dinâmica
Interpretação qualitativa do SHAP por percentis (alto / moderado / baixo impacto) + direção (+/- probabilidade de clonagem).

### Zonas Quentes / Georreferenciamento
Mapeamento de coordenadas para 20 cidades de SC, cálculo de distância (Haversine) e marcação contextual.

### Deduplicação de Alertas
Hash de conteúdo semântico para evitar múltiplos alertas equivalentes na mesma janela.

---

## 5. Sistema de Alertas JSON-LD
Estrutura semântica com contexto versionado, incluindo classificação automática (severidade, urgência, certeza) derivada do score.

Exemplo (resumido):
```json
{
  "@context": "https://www.mopred.org/schemas/alerta/v1",
  "@type": "AlertaPreditivo",
  "id": "urn:uuid:...",
  "identificadorSistema": "MOPRED-SC-01",
  "timestampEmissao": "2025-08-13T00:39:48Z",
  "info": { "evento": "Comportamento Veicular Suspeito", "severidade": "Alta" },
  "recursos": [{"descricaoRecurso": "Contexto da Inferência", "conteudo": {"metodo": "SHAP"}}]
}
```

Arquivos gerados:
* `alertas_janela_XXX.ndjson`
* `alertas_consolidados.ndjson`
* `alertas_gerados.ndjson` (explicabilidade agregada)

---

## 6. Estrutura de Diretórios (Essencial)
```
configs/                # Configurações principais
csvs/                   # Saídas e datasets sintéticos
alertas_gerados/        # Alertas JSON-LD por janela + consolidados
validacao_modelo_conceitual.py
simulador_streaming_alpr.py
comparador_modelos.py
alertas.py
gerador_veiculos.py
utils.py
```

Arquivo histórico preservado em `docs_historicas/descricao.md` (conteúdo agora incorporado aqui).

---

## 7. Configurações Atuais (`configs/config.json`)

### Parâmetros Principais
```json
{
  "csv_veiculos_path": "csvs/veiculos_gerados_com_clones.csv",
  "total_veiculos": 5000,
  "percentual_veiculos_clonados": 0.02,
  "n_sensores": 200,
  "intervalo_tempo_simulacao_horas": 6,
  "timestamp_inicio": "2025-08-01T00:00:00"
}
```

### Modelos e Privacidade
```json
{
  "n_jobs": 4,
  "usar_smote": false,
  "smote_k_neighbors": 5,
  "usar_pseudonimizacao": true,
  "salt_pseudonimizacao": "mopred_doutorado_2024_chave_secreta"
}
```

### Alertas
```json
{
  "gerar_alertas": true,
  "limiar_alertas": 0.80,
  "identificador_sistema_alertas": "MOPRED-SC-01",
  "pasta_alertas": "alertas_gerados"
}
```

### Organização
```json
{
  "pasta_csvs": "csvs"
}
```

### Cidades e Zonas
* 20 cidades SC mapeadas (Florianópolis, Joinville, Blumenau, Chapecó, Criciúma, Itajaí, São José, Lages, Palhoça, Balneário Camboriú, ...)
* Zonas quentes padrão: Florianópolis, Chapecó, Criciúma

---

## 8. Métricas e Monitoramento
* Accuracy, Precision, Recall, F1 (por janela)
* Evolução temporal vs. modelo adaptativo
* Impacto das features via SHAP
* Detecção implícita de drift (quedas abruptas / recuperação adaptativa)

---

## 9. Explicabilidade (SHAP)
* Cálculo por janela para casos positivos
* Interpretação categorizada (Alto / Moderado / Baixo impacto)
* Integração direta nos alertas (campo recursos)
* Consolidação final em `alertas_gerados.ndjson`

---

## 10. Evoluções e Correções Relevantes
| Problema | Solução |
|----------|---------|
| Duplicação de alertas (janela 007) | Deduplicação por hash de conteúdo |
| Erro SHAP (arrays numpy heterogêneos) | Normalização e conversão segura |
| Cidades aparecendo N/A | Mapeamento coordenadas → cidade mais próxima |

Outras: reorganização de pastas, parametrização completa de caminhos, robustez em pseudonimização.

---

## 11. Segurança e Privacidade
* Pseudonimização HMAC-SHA256 com salt configurável
* Logs sem dados sensíveis diretos
* Reprodutibilidade preservada sem reversibilidade de placas

---

## 12. Limitações Atuais
* Near-real-time baseado em micro-batches (não streaming evento-a-evento)
* Limiar fixo por configuração (não adaptativo ainda)
* Ausência de detecção explícita formal de drift (implícita via métricas)

### Próximos Passos Sugeridos
1. Ajuste dinâmico de limiar (calibração por janela)
2. Módulo de detecção de concept drift dedicado
3. Persistência incremental de estado adaptativo entre execuções
4. Painel interativo (dashboard) para métricas e alertas
5. Integração opcional com mensageria (Kafka / MQTT)

---

## 13. Como Executar
```bash
python validacao_modelo_conceitual.py         # Execução principal
python gerador_veiculos.py                    # Geração de dataset sintético
python testes/validacao_alertas/testar_alertas.py
```

### Passos para Configuração Customizada
1. Editar `configs/config.json`
2. (Opcional) Regenerar veículos
3. Rodar pipeline principal
4. Inspecionar `alertas_gerados/` e métricas em CSV

---

## 14. Estado Atual
* Núcleo funcional completo
* Documentação unificada
* Pronto para experimentos acadêmicos e extensão

---

**MOPRED – Sistema de Detecção de Clonagem Veicular**  
Desenvolvido para Tese de Doutorado – 2025  
Documentação Consolidada v2.2.0

