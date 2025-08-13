# MOPRED - Sistema de Detecção de Clonagem Veicular
## Documentação Completa e Organizada

---

# 📋 1. VISÃO GERAL DO PROJETO

## Objetivos Principais

Este sistema implementa uma solução completa para detecção de clonagem veicular usando tecnologias de **Machine Learning adaptativo** e **Explicabilidade Artificial (XAI)**. O projeto simula um ambiente real de monitoramento por câmeras ALPR (Automatic License Plate Recognition) e compara diferentes abordagens de detecção ao longo do tempo.

### 🎯 Metas do Sistema
1. **Comparar modelos tradicionais vs. adaptativos** para detecção de clonagem
2. **Analisar o impacto de features multimodais** (infrações + semelhança visual)  
3. **Implementar explicabilidade** usando SHAP Values
4. **Simular mudanças temporais** nos padrões de clonagem
5. **Garantir privacidade** através de pseudonimização
6. **Processamento near-real-time** com arquitetura de micro-batches
7. **Geração de alertas padronizados** em formato JSON-LD com explicabilidade integrada

---

# 🏗️ 2. ARQUITETURA DO SISTEMA

## Componentes Principais

### 2.1 Simulador de Streaming ALPR
- Gera eventos de passagem de veículos em câmeras distribuídas
- Simula rotas urbanas e intermunicipais realistas de Santa Catarina
- Inclui veículos legítimos e clonados com padrões específicos
- Processamento temporal em micro-batches para análise near-real-time

### 2.2 Sistema de Features Multimodais
```python
# Features básicas (3 dimensões)
[distância_km, tempo_segundos, velocidade_kmh]

# Features multimodais (7 dimensões)  
[distância_km, tempo_segundos, velocidade_kmh, 
 num_infrações, marca_modelo_igual, tipo_igual, cor_igual]
```

### 2.3 Modelos de Machine Learning
- **Random Forest Tradicional**: Treino estático inicial
- **Adaptive Random Forest**: Aprendizado incremental online
- **Variações**: Básico (3 features) vs. Multimodal (7 features)

### 2.4 Sistema de Alertas JSON-LD
- Geração automática conforme especificação acadêmica
- Integração de explicabilidade XAI nos alertas
- Classificação automática por severidade, urgência e certeza
- Formato semântico estruturado com contexto JSON-LD

---

# 🔄 3. FLUXO DE EXECUÇÃO

## 3.1 Fase 1: Preparação dos Dados
```
1. Geração de eventos simulados
2. Aplicação de pseudonimização (opcional)
3. Divisão em fases temporais com características diferentes
4. Balanceamento com SMOTE (opcional)
```

## 3.2 Fase 2: Treinamento Inicial
```
1. Extração de features de pares de eventos
2. Treinamento de 2 modelos tradicionais:
   - Básico (3 features)
   - Multimodal (7 features)
3. Inicialização do modelo adaptativo
```

## 3.3 Fase 3: Simulação Temporal
```
Para cada janela temporal (micro-batch):
1. Treino incremental do modelo adaptativo
2. Avaliação de todos os modelos
3. Coleta de métricas (accuracy, precision, recall, F1)
4. Análise de drift nos padrões
5. Processamento near-real-time dos eventos
```

## 3.4 Fase 4: Análise e Explicabilidade
```
1. Geração de relatórios comparativos
2. Explicação SHAP dos casos clonados
3. Interpretação dinâmica dos impactos
4. Visualização de resultados
5. Geração automática de alertas JSON-LD
6. Consolidação e arquivamento de alertas
```

---

# 🧠 4. FUNCIONALIDADES AVANÇADAS

## 4.1 Pseudonimização Segura
```python
def pseudonimizar_placa(placa, salt):
    # Usa HMAC + SHA-256 para gerar pseudônimos irreversíveis
    # Exemplo: "ABC1234" → "PSEUDO_A1B2C3D4"
    hash_obj = hmac.new(salt.encode('utf-8'), 
                       placa.encode('utf-8'), 
                       hashlib.sha256)
    return f"PSEUDO_{hash_obj.hexdigest()[:8].upper()}"
```

## 4.2 Balanceamento Inteligente
- **SMOTE adaptativo**: Balanceia classes automaticamente
- **Configurável**: Pode ser habilitado/desabilitado via config
- **k_neighbors adaptativo**: Ajusta baseado no tamanho da menor classe

## 4.3 Mapeamento Geográfico Inteligente
- Sistema de coordenadas para 20 cidades de Santa Catarina
- Cálculo de distância usando fórmula de Haversine
- Mapeamento automático de coordenadas para cidades mais próximas
- Zonas quentes configuráveis para análise de padrões regionais

---

# 🚨 5. SISTEMA DE ALERTAS JSON-LD

## 5.1 Visão Geral
O sistema gera alertas padronizados em JSON-LD conforme especificação da tese de doutorado. Os alertas incluem explicabilidade XAI integrada e são classificados automaticamente.

## 5.2 Estrutura do Alerta JSON-LD
```json
{
  "@context": "https://www.mopred.org/schemas/alerta/v1",
  "@type": "AlertaPreditivo",
  "id": "urn:uuid:...",
  "identificadorSistema": "MOPRED-SC-01",
  "timestampEmissao": "2025-08-13T00:39:48Z",
  "status": "Real",
  "escopo": "Restrito",
  
  "info": {
    "evento": "Comportamento Veicular Suspeito",
    "severidade": "Alta|Média|Baixa",
    "urgencia": "Imediata|Próxima|Rotina",
    "certeza": "Provável|Possível|Indeterminado",
    "descricao": "Descrição automática baseada no score",
    "instrucao": "Instruções operacionais",
    "parametrosPreditivos": [...]
  },
  
  "area": {
    "descricaoArea": "Localização geográfica",
    "geometria": {
      "@type": "Ponto",
      "coordenadas": [lat, lon]
    }
  },
  
  "recursos": [
    {
      "descricaoRecurso": "Contexto da Inferência",
      "mimeType": "application/json",
      "conteudo": {
        "explicabilidade": "Dados SHAP integrados",
        "confianca": "Score de predição",
        "contexto": "Metadados do evento"
      }
    }
  ]
}
```

## 5.3 Características dos Alertas
- **Geração Automática**: Durante processamento de janelas temporais
- **Explicabilidade XAI**: Valores SHAP integrados nos alertas
- **Classificação Inteligente**: Severidade, urgência e certeza automáticas
- **Deduplicação**: Sistema evita alertas duplicados
- **Pasta Configurável**: Salvamento em pasta configurada via `config.json`

---

# 📁 6. ESTRUTURA DO PROJETO

## 6.1 Estrutura Final Organizada

```
d:\Workspace\mopred\
├── 📂 configs/                           # Configurações
│   ├── config.json                      # Configuração principal
│   └── caracteristicas_veiculos.json    # Especificações de veículos
├── 📂 csvs/                              # Dados CSV organizados
│   ├── comparacao_modelos_resultados.csv
│   ├── passagens.csv
│   ├── passagens_streaming.csv
│   ├── veiculos_gerados_com_clones.csv
│   └── veiculos_gerados_sem_infracao.csv
├── 📂 alertas_gerados/                   # Alertas JSON-LD
│   ├── alertas_consolidados.ndjson
│   ├── alertas_gerados.ndjson
│   ├── alertas_janela_001.ndjson
│   ├── alertas_janela_002.ndjson
│   └── ... (outros arquivos de janela)
├── 📂 testes/                            # Testes organizados
│   ├── 📄 README.md
│   ├── 📂 correcoes_cidades/             # Correção do mapeamento
│   │   ├── debug_cidades.py
│   │   ├── teste_correcao_cidades.py
│   │   ├── teste_alertas_cidades.py
│   │   └── verificar_correcao_final.py
│   ├── 📂 validacao_alertas/             # Validação de alertas
│   │   ├── testar_alertas.py
│   │   ├── testar_formatacao_alertas.py
│   │   ├── teste_pasta_alertas.py
│   │   ├── validar_pasta_alertas.py
│   │   ├── validar_correcoes.py
│   │   └── verificar_correcoes.py
│   ├── 📂 debug_geral/                   # Debug geral
│   │   ├── debug_processamento.py
│   │   └── verificar_caracteristicas_clones.py
│   └── 📂 demos/                         # Demonstrações
│       └── demo_controle_alertas.py
├── 📄 validacao_modelo_conceitual.py     # Arquivo principal
├── 📄 alertas.py                         # Sistema de alertas
├── 📄 comparador_modelos.py              # Comparador de modelos
├── 📄 simulador_streaming_alpr.py        # Simulador principal
├── 📄 gerador_veiculos.py                # Gerador de veículos
├── 📄 utils.py                           # Utilitários
└── 📄 README.md                          # Esta documentação
```

---

# ⚙️ 7. CONFIGURAÇÃO DO SISTEMA

## 7.1 Arquivo configs/config.json

### Configurações Principais
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

### Configurações de Modelos
```json
{
  "n_jobs": 4,
  "usar_smote": false,
  "smote_k_neighbors": 5,
  "usar_pseudonimizacao": true,
  "salt_pseudonimizacao": "mopred_doutorado_2024_chave_secreta"
}
```

### Configurações de Alertas
```json
{
  "gerar_alertas": true,
  "limiar_alertas": 0.80,
  "identificador_sistema_alertas": "MOPRED-SC-01",
  "pasta_alertas": "alertas_gerados"
}
```

### Configurações de Organização
```json
{
  "pasta_csvs": "csvs"
}
```

## 7.2 Cidades de Santa Catarina
O sistema trabalha com 20 cidades principais de SC, incluindo coordenadas geográficas e distribuição de sensores:

**Cidades Principais**: Florianópolis, Joinville, Blumenau, Chapecó, Itajaí, São José, Criciúma, Lages, Palhoça, Balneário Camboriú

**Zonas Quentes**: Florianópolis, Chapecó, Criciúma (configuráveis)

---

# 🧪 8. SISTEMA DE TESTES

## 8.1 Categorias de Testes

### Correções de Cidades (`testes/correcoes_cidades/`)
- `debug_cidades.py` - Debug do mapeamento de coordenadas
- `teste_correcao_cidades.py` - Validação do sistema de cidades
- `teste_alertas_cidades.py` - Teste de alertas com cidades corretas

### Validação de Alertas (`testes/validacao_alertas/`)
- `testar_alertas.py` - Teste principal do módulo de alertas
- `testar_formatacao_alertas.py` - Teste de formatação JSON-LD
- `validar_pasta_alertas.py` - Validação do sistema de pastas

### Debug Geral (`testes/debug_geral/`)
- `debug_processamento.py` - Debug do pipeline principal
- `verificar_caracteristicas_clones.py` - Verificação de características

### Demonstrações (`testes/demos/`)
- `demo_controle_alertas.py` - Demo do controle de alertas

## 8.2 Como Executar Testes
```bash
cd "d:\Workspace\mopred"
python testes/[categoria]/[arquivo].py
```

---

# 🔧 9. FUNCIONALIDADES IMPLEMENTADAS

## 9.1 Organização de Arquivos
- ✅ **Configurações**: Pasta `configs/` para arquivos de configuração
- ✅ **CSVs**: Pasta `csvs/` para dados tabulares
- ✅ **Alertas**: Pasta `alertas_gerados/` para alertas JSON-LD
- ✅ **Testes**: Pasta `testes/` com subcategorias organizadas

## 9.2 Sistema de Alertas
- ✅ **Geração Automática**: Alertas criados durante processamento
- ✅ **Formato JSON-LD**: Padrão semântico estruturado
- ✅ **Explicabilidade XAI**: Valores SHAP integrados
- ✅ **Deduplicação**: Evita alertas duplicados
- ✅ **Pasta Configurável**: Salvamento flexível

## 9.3 Mapeamento Geográfico
- ✅ **20 Cidades SC**: Coordenadas e distribuição de sensores
- ✅ **Cálculo de Distâncias**: Fórmula de Haversine
- ✅ **Zonas Quentes**: Áreas de maior atenção configuráveis
- ✅ **Mapeamento Inteligente**: Coordenadas → cidade mais próxima

## 9.4 Processamento de Dados
- ✅ **Pseudonimização**: HMAC + SHA-256 para privacidade
- ✅ **SMOTE Balanceamento**: Classes balanceadas automaticamente
- ✅ **Features Multimodais**: 7 dimensões incluindo semelhança visual
- ✅ **Processamento Paralelo**: n_jobs configurável

## 9.5 Modelos Adaptativos
- ✅ **Random Forest Tradicional**: Baseline estático
- ✅ **Adaptive Random Forest**: Aprendizado incremental
- ✅ **Comparação Automática**: Métricas lado a lado
- ✅ **Análise Temporal**: Janelas de processamento

---

# 🎯 10. PRINCIPAIS EVOLUÇÕES DO PROJETO

## 10.1 Correção de Problemas Técnicos
- **Problema**: Alertas duplicados na janela 007 (~2000 linhas)
- **Solução**: Sistema de deduplicação baseado em conteúdo

- **Problema**: Erro SHAP com arrays numpy
- **Solução**: Tratamento robusto de diferentes tipos de dados SHAP

- **Problema**: Cidades aparecendo como "N/A" nos alertas
- **Solução**: Sistema de mapeamento coordenadas → cidades

## 10.2 Organizações Estruturais
- **Implementação**: Sistema de pastas configuráveis para alertas
- **Implementação**: Organização completa dos arquivos de teste
- **Implementação**: Pasta dedicada para arquivos CSV
- **Implementação**: Renomeação do arquivo principal para contexto acadêmico

## 10.3 Melhorias de Funcionalidade
- **Sistema de Alertas JSON-LD**: Formato padronizado com explicabilidade
- **Mapeamento Geográfico**: 20 cidades de SC com coordenadas precisas
- **Pseudonimização**: Privacidade garantida com salt configurável
- **Configuração Flexível**: Sistema completamente configurável via JSON

---

# 🚀 11. COMO USAR O SISTEMA

## 11.1 Execução Principal
```bash
cd "d:\Workspace\mopred"
python validacao_modelo_conceitual.py
```

## 11.2 Configuração Personalizada
1. Edite `configs/config.json` conforme necessário
2. Ajuste parâmetros de modelos, alertas e organização
3. Execute o sistema principal

## 11.3 Geração de Veículos
```bash
python gerador_veiculos.py
```

## 11.4 Execução de Testes Específicos
```bash
python testes/validacao_alertas/testar_alertas.py
python testes/correcoes_cidades/teste_correcao_cidades.py
```

---

# 📊 12. MÉTRICAS E RESULTADOS

## 12.1 Métricas Coletadas
- **Accuracy**: Precisão geral dos modelos
- **Precision**: Precisão para detecção de clonagem
- **Recall**: Taxa de detecção de casos clonados
- **F1-Score**: Média harmônica precision/recall
- **Análise Temporal**: Evolução das métricas por janela

## 12.2 Comparações Realizadas
- **Tradicional vs. Adaptativo**: Modelos estáticos vs. incrementais
- **Básico vs. Multimodal**: 3 vs. 7 features
- **Com/Sem SMOTE**: Impacto do balanceamento
- **Com/Sem Pseudonimização**: Análise de privacidade

## 12.3 Explicabilidade XAI
- **Valores SHAP**: Contribuição de cada feature
- **Interpretação Dinâmica**: Impacto alto/médio/baixo
- **Casos Clonados**: Análise detalhada dos fatores decisivos
- **Integração em Alertas**: Explicabilidade diretamente nos alertas

---

# 🎉 13. STATUS ATUAL DO PROJETO

## ✅ Funcionalidades Completamente Implementadas
- Sistema de detecção de clonagem com modelos adaptativos
- Geração automática de alertas JSON-LD com explicabilidade XAI
- Mapeamento geográfico inteligente para Santa Catarina
- Organização completa de arquivos e configurações
- Sistema de testes abrangente e organizado
- Pseudonimização segura para proteção de privacidade
- Processamento near-real-time com micro-batches

## 🏆 Principais Conquistas
- **Estrutura Profissional**: Projeto organizado para contexto acadêmico
- **Padrões de Qualidade**: Código limpo e bem documentado
- **Flexibilidade**: Sistema completamente configurável
- **Explicabilidade**: XAI integrado em todo o pipeline
- **Escalabilidade**: Arquitetura preparada para expansão

## 🚀 Pronto Para Uso
O sistema está **completamente funcional** e pronto para:
- Análises acadêmicas e experimentação
- Desenvolvimento de pesquisas em detecção de clonagem
- Demonstrações e apresentações
- Extensões e melhorias futuras

---

**MOPRED - Sistema de Detecção de Clonagem Veicular**  
*Desenvolvido para Tese de Doutorado - 2025*  
*Versão: 2.1.3 - Documentação Consolidada*
