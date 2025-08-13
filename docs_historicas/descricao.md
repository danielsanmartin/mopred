# Sistema de Detecção de Clonagem Veicular com Modelos Adaptativos

## 📋 Visão Geral

Este sistema implementa uma solução completa para detecção de clonagem veicular usando tecnologias de **Machine Learning adaptativo** e **Explicabilidade Artificial (XAI)**. O projeto simula um ambiente real de monitoramento por câmeras ALPR (Automatic License Plate Recognition) e compara diferentes abordagens de detecção ao longo do tempo.

## 🎯 Objetivos Principais

1. **Comparar modelos tradicionais vs. adaptativos** para detecção de clonagem
2. **Analisar o impacto de features multimodais** (infrações + semelhança visual)
3. **Implementar explicabilidade** usando SHAP Values
4. **Simular mudanças temporais** nos padrões de clonagem
5. **Garantir privacidade** através de pseudonimização
6. **Processamento near-real-time** com arquitetura de micro-batches para análise temporal contínua
7. **Geração de alertas padronizados** em formato JSON-LD com explicabilidade integrada

## 🏗️ Arquitetura do Sistema

### 1. **Simulador de Streaming ALPR**
- Gera eventos de passagem de veículos em câmeras distribuídas
- Simula rotas urbanas e intermunicipais realistas
- Inclui veículos legítimos e clonados com padrões específicos
- Processamento temporal em micro-batches para análise near-real-time

### 2. **Sistema de Features Multimodais**
```python
# Features básicas (3 dimensões)
[distância_km, tempo_segundos, velocidade_kmh]

# Features multimodais (7 dimensões)
[distância_km, tempo_segundos, velocidade_kmh, 
 num_infrações, marca_modelo_igual, tipo_igual, cor_igual]
```

### 3. **Modelos de Machine Learning**
- **Random Forest Tradicional**: Treino estático inicial
- **Adaptive Random Forest**: Aprendizado incremental online
- **Variações**: Básico (3 features) vs. Multimodal (7 features)

### 4. **Sistema de Alertas JSON-LD**
- Geração automática de alertas padronizados conforme especificação acadêmica
- Integração de explicabilidade XAI nos alertas
- Classificação automática por severidade, urgência e certeza
- Formato semântico estruturado com contexto JSON-LD

## 🔄 Fluxo de Execução

### **Fase 1: Preparação dos Dados**
```
1. Geração de eventos simulados
2. Aplicação de pseudonimização (opcional)
3. Divisão em fases temporais com características diferentes
4. Balanceamento com SMOTE (opcional)
```

### **Fase 2: Treinamento Inicial**
```
1. Extração de features de pares de eventos
2. Treinamento de 2 modelos tradicionais:
   - Básico (3 features)
   - Multimodal (7 features)
3. Inicialização do modelo adaptativo
```

### **Fase 3: Simulação Temporal**
```
Para cada janela temporal (micro-batch):
1. Treino incremental do modelo adaptativo
2. Avaliação de todos os modelos
3. Coleta de métricas (accuracy, precision, recall, F1)
4. Análise de drift nos padrões
5. Processamento near-real-time dos eventos
```

### **Fase 4: Análise e Explicabilidade**
```
1. Geração de relatórios comparativos
2. Explicação SHAP dos casos clonados
3. Interpretação dinâmica dos impactos
4. Visualização de resultados
5. Geração automática de alertas JSON-LD
6. Consolidação e arquivamento de alertas
```

## 🧠 Funcionalidades Avançadas

### **1. Pseudonimização Segura**
```python
def pseudonimizar_placa(placa, salt):
    # Usa HMAC + SHA-256 para gerar pseudônimos irreversíveis
    # Exemplo: "ABC1234" → "PSEUDO_A1B2C3D4"
    hash_obj = hmac.new(salt.encode('utf-8'), 
                       placa.encode('utf-8'), 
                       hashlib.sha256)
    return f"PSEUDO_{hash_obj.hexdigest()[:8].upper()}"
```

### **2. Balanceamento Inteligente**
- **SMOTE adaptativo**: Balanceia classes automaticamente
- **Configurável**: Pode ser habilitado/desabilitado via config
- **Robusto**: Verifica condições mínimas antes de aplicar

### **3. Explicabilidade com SHAP**
```python
# Interpretação dinâmica baseada em percentis
def interpretar_impacto_shap_dinamico(valor_shap, todos_valores):
    p60 = np.percentile(abs_todos, 60)  # Threshold alto
    p30 = np.percentile(abs_todos, 30)  # Threshold baixo
    
    if abs_valor >= p60:
        return "🔴 + Alto impacto"    # Aumenta probabilidade
    elif abs_valor >= p30:
        return "🟡 + Impacto moderado" # Impacto médio
    else:
        return "🟢 + Baixo impacto"    # Pouca influência
```

### **4. Zonas Quentes Configuráveis**
```python
# Define regiões com maior probabilidade de clonagem
zonas_quentes = ["Florianópolis", "Chapecó", "Criciúma"]
raio_zona = 0.2  # ~20km de raio

# Aplica marcação automática baseada em coordenadas do config.json
for evento in eventos:
    if evento_em_zona_quente(evento, zonas_quentes):
        evento.is_clonado = True
```

### **5. Geração de Alertas Padronizados**
```python
# Gera alertas JSON-LD automaticamente para casos suspeitos
def criar_alerta(passagem, explicabilidade):
    alerta = {
        "@context": "https://www.mopred.org/schemas/alerta/v1",
        "@type": "AlertaPreditivo",
        "info": {
            "evento": "Comportamento Veicular Suspeito",
            "escoreSuspeicao": passagem["escore"],
            "explicabilidade": explicabilidade
        },
        "recursos": [...]  # Contexto da inferência e evidências
    }
    return alerta
```

## 📊 Métricas e Avaliação

### **Métricas Coletadas**
- **Accuracy**: Precisão geral do modelo
- **Precision**: Taxa de verdadeiros positivos
- **Recall**: Capacidade de detectar clonagem
- **F1-Score**: Média harmônica de precision e recall

### **Cenários Avaliados**
1. **Tradicional Básico**: 3 features, treino estático
2. **Tradicional Multimodal**: 7 features, treino estático
3. **Adaptativo Básico**: 3 features, aprendizado incremental
4. **Adaptativo Multimodal**: 7 features, aprendizado incremental

## 🔧 Configuração Flexível

### **Arquivo `config.json`**
```json
{
  "usar_smote": true,                    // Balanceamento automático
  "smote_k_neighbors": 5,               // Parâmetro do SMOTE
  "usar_pseudonimizacao": false,        // Privacidade das placas
  "salt_pseudonimizacao": "chave_secreta", // Salt para hash
  "zonas_quentes": ["Florianópolis"],   // Regiões de interesse
  "raio_zonas_quentes": 0.2,           // Raio em graus (~20km)
  "n_jobs": 8                          // Paralelização
}
```

## 🎯 Principais Inovações

### **1. Aprendizado Adaptativo**
- Modelo se adapta automaticamente a novos padrões de clonagem
- Não requer retreinamento completo
- Mantém conhecimento anterior enquanto aprende novos comportamentos

### **2. Features Multimodais Inteligentes**
- Combina dados físicos (velocidade, distância) com semânticos (cor, modelo)
- Decomposição de semelhança em features binárias interpretáveis
- Inclusão de histórico de infrações como indicador comportamental

### **3. Explicabilidade Contextual**
- SHAP values com interpretação dinâmica
- Thresholds adaptativos baseados na distribuição de cada caso
- Indicação de direção do impacto (positivo/negativo)

### **4. Simulação Realística**
- Rotas baseadas em coordenadas reais de Santa Catarina
- Padrões temporais de clonagem evolutivos
- Zonas quentes configuráveis geograficamente

### **5. Processamento Near-Real-Time**
- Arquitetura de micro-batches para análise temporal contínua
- Processamento por janelas temporais sequenciais
- Adaptação incremental sem necessidade de retreinamento completo
- Capacidade de processamento de eventos em fluxo temporal estruturado

### **6. Sistema de Alertas Inteligentes**
- Geração automática de alertas JSON-LD para casos suspeitos
- Classificação automática por severidade (Alta/Média/Baixa)
- Integração de explicabilidade XAI em cada alerta
- Consolidação e arquivamento estruturado por janelas temporais

## 📈 Resultados Esperados

### **Hipóteses de Pesquisa**
1. **Modelos adaptativos** superarão tradicionais em cenários dinâmicos
2. **Features multimodais** melhorarão significativamente a detecção
3. **Explicabilidade** revelará insights sobre padrões de clonagem
4. **Pseudonimização** manterá utilidade dos dados preservando privacidade

### **Métricas de Sucesso**
- F1-Score > 0.85 para modelos multimodais
- Adaptação rápida a novos padrões (< 3 janelas)
- Explicações SHAP coerentes com conhecimento do domínio
- Zero recuperação de placas originais após pseudonimização

## 🛡️ Aspectos de Segurança e Privacidade

### **Pseudonimização Robusta**
- Algoritmo HMAC-SHA256 com salt configurável
- Impossibilidade de engenharia reversa
- Manutenção de consistência para análises longitudinais

### **Configuração Segura**
- Salt armazenado separadamente em produção
- Logs sem informações sensíveis
- Configuração granular de privacidade

## 🚀 Aplicações Práticas

### **Segurança Pública**
- Detecção automática de veículos clonados em near-real-time
- Análise de padrões criminais emergentes
- Suporte à investigação policial com processamento temporal contínuo

### **Pesquisa Acadêmica**
- Benchmark para algoritmos adaptativos
- Estudo de concept drift em segurança
- Validação de técnicas XAI em domínios críticos
- Análise de processamento temporal em micro-batches

### **Sistemas Comerciais**
- Integração com sistemas ALPR existentes
- Alertas inteligentes para operadores
- Dashboards de monitoramento em tempo real
- Arquitetura escalável para processamento contínuo

## 📁 Estrutura de Arquivos

### **Arquivos Principais**
- `teste_modelos_temporais.py` - Script principal com análise completa
- `simulador_streaming_alpr.py` - Simulador de eventos ALPR
- `comparador_modelos.py` - Framework de comparação de modelos
- `alertas.py` - Módulo de geração de alertas JSON-LD padronizados
- `gerador_veiculos.py` - Geração de dados sintéticos de veículos
- `config.json` - Configuração flexível do sistema

### **Arquivos de Dados**
- `veiculos_gerados_com_clones.csv` - Dataset de veículos sintéticos
- `passagens.csv` - Eventos de passagem simulados
- `comparacao_modelos_resultados.csv` - Resultados das comparações

### **Arquivos de Alertas**
- `alertas_janela_XXX.ndjson` - Alertas por janela temporal
- `alertas_consolidados.ndjson` - Todos os alertas consolidados
- `alertas_gerados.ndjson` - Alertas do relatório SHAP final

### **Utilitários**
- `utils.py` - Funções auxiliares de processamento
- `random_forest.py` - Implementações específicas de RF
- `debug_processamento.py` - Ferramentas de depuração
- `testar_alertas.py` - Script de teste do sistema de alertas
- `README_ALERTAS.md` - Documentação do sistema de alertas

## 🔬 Configuração para Pesquisa

### **Parâmetros Geo-Específicos (Santa Catarina)**
```json
"lat_lon_por_cidade": {
  "Florianópolis": [-27.5954, -48.5480],
  "Joinville": [-26.3045, -48.8487],
  "Blumenau": [-26.9156, -49.0706],
  "Chapecó": [-27.1000, -52.6152],
  // ... 16 cidades mais
},
"zonas_quentes": ["Florianópolis", "Chapecó", "Criciúma"],
"sensores_por_cidade": {
  "Florianópolis": 24,  // Maior densidade de sensores
  "Joinville": 20,
  "Blumenau": 16
  // ... distribuição realística
}
```

### **Parâmetros de Simulação**
```json
"total_veiculos": 5000,
"percentual_veiculos_clonados": 0.02,     // 2% clonados
"intervalo_tempo_simulacao_horas": 6,      // Janela de observação
"chance_de_rotas_urbanas": 0.8,           // 80% tráfego urbano
"intervalo_infracoes_clonado": [5, 20],   // Clones mais infrações
"intervalo_infracoes_normal": [0, 3]      // Veículos normais
```

## 🎓 Aplicação Acadêmica

Este sistema foi desenvolvido especificamente para pesquisa acadêmica em:

- **Detecção de Anomalias Temporais**
- **Machine Learning Adaptativo**
- **Explicabilidade em Sistemas Críticos**
- **Privacidade e Anonimização**
- **Análise de Concept Drift**

### **Contribuições Científicas**
1. Framework comparativo entre modelos estáticos e adaptativos
2. Metodologia de features multimodais para detecção de clonagem
3. Técnicas de explicabilidade contextual com SHAP
4. Protocolo de pseudonimização para dados sensíveis
5. Simulação georreferenciada realística
6. Arquitetura de processamento near-real-time com micro-batches para análise temporal
7. Sistema padronizado de alertas JSON-LD com explicabilidade integrada

## 🚨 Sistema de Alertas JSON-LD

### **Características dos Alertas**
- **Formato Padronizado**: JSON-LD conforme especificação acadêmica
- **Contexto Semântico**: Schema estruturado com @context versionado
- **Explicabilidade Integrada**: SHAP values e fatores de risco inclusos
- **Classificação Automática**: Severidade, urgência e certeza baseadas no score
- **Rastreabilidade**: UUID único e timestamps ISO8601 para auditoria

### **Estrutura do Alerta**
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
    "parametrosPreditivos": [
      {"nome": "escoreSuspeicao", "valor": "0.92", "metrica": "Probabilidade"}
    ]
  },
  
  "area": {
    "descricaoArea": "Localização do evento",
    "geometria": {"@type": "Ponto", "coordenadas": [lat, lon]}
  },
  
  "recursos": [
    {
      "descricaoRecurso": "Contexto da Inferência",
      "mimeType": "application/json",
      "conteudo": {
        "idModelo": "RF-v2.1.3",
        "metodo": "SHAP",
        "contribuicoes": [...],
        "fatoresDeRisco": [...]
      }
    }
  ]
}
```

### **Processamento Automático**
- **Por Janela Temporal**: Alertas gerados durante avaliação de cada janela
- **Limiar Configurável**: Score mínimo para geração de alerta (padrão: 0.80)
- **Consolidação**: Todos os alertas são consolidados em arquivo único
- **Arquivamento**: Organização estruturada por janelas e timestamps

### **Arquivos de Saída**
```
alertas_janela_001.ndjson     # Alertas da janela temporal 1
alertas_janela_002.ndjson     # Alertas da janela temporal 2
alertas_consolidados.ndjson   # Todos os alertas consolidados
alertas_gerados.ndjson        # Alertas com explicabilidade SHAP
```

## ⚡ Características de Processamento Temporal

### **Arquitetura Near-Real-Time**
- **Processamento por Micro-Batches**: Eventos agrupados em janelas temporais para análise eficiente
- **Adaptação Incremental**: Modelos se atualizam continuamente sem retreinamento completo
- **Fluxo Temporal Estruturado**: Sequenciamento de eventos mantém ordem cronológica
- **Análise de Drift**: Detecção automática de mudanças nos padrões ao longo do tempo

### **Limitações Arquiteturais**
- **Classificação**: Near-real-time (PARCIAL) - não orientado a eventos individuais
- **Processamento**: Baseado em micro-batches, não em streaming puro
- **Latência**: Dependente do tamanho da janela temporal configurada
- **Escalabilidade**: Adequada para análise temporal, limitada para alertas instantâneos

---

Este sistema representa uma abordagem estado-da-arte para detecção de clonagem veicular, combinando **machine learning adaptativo**, **explicabilidade artificial**, **preservação de privacidade** e **alertas padronizados** em uma solução integrada e configurável para pesquisa e aplicação prática. O sistema de alertas JSON-LD garante interoperabilidade semântica e rastreabilidade completa para uso em ambientes operacionais e acadêmicos.
