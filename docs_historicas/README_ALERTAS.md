# Sistema de Alertas JSON-LD para Detecção de Clonagem Veicular

## 📋 Visão Geral

O sistema foi evoluído para incluir geração automática de alertas padronizados em JSON-LD conforme especificação da tese de doutorado. Os alertas são gerados automaticamente durante o processamento de janelas temporais e incluem explicabilidade XAI.

## 🏗️ Arquitetura do Sistema de Alertas

### Componentes Principais

1. **`alertas.py`** - Módulo principal de geração de alertas
2. **`GeradorAlertasSimples`** - Classe para geração de alertas individuais e em lote
3. **`extrair_explicabilidade_shap`** - Função para extrair explicabilidade SHAP
4. **Integração no pipeline** - Geração automática durante avaliação de janelas

### Estrutura do Alerta JSON-LD

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
        "idModelo": "RF-v2.1.3",
        "metodo": "SHAP",
        "contribuicoes": [...],
        "fatoresDeRisco": [...]
      }
    }
  ]
}
```

## 🚀 Uso do Sistema

### 1. Geração Automática (Integrada ao Pipeline)

O sistema gera alertas automaticamente durante a execução do `teste_modelos_temporais.py`:

```bash
python teste_modelos_temporais.py
```

**Controle via configuração:**
```json
{
  "gerar_alertas": true,     // Para habilitar
  "limiar_alertas": 0.80,    // Score mínimo
}
```

**Para desabilitar alertas:**
```json
{
  "gerar_alertas": false
}
```

**Saídas geradas (quando habilitado):**
- `alertas_janela_001.ndjson`, `alertas_janela_002.ndjson`, ... - Alertas por janela
- `alertas_consolidados.ndjson` - Todos os alertas consolidados
- `alertas_gerados.ndjson` - Alertas do relatório SHAP final

### 2. Uso Programático

```python
from alertas import GeradorAlertasSimples, extrair_explicabilidade_shap

# Criar gerador
gerador = GeradorAlertasSimples(
    identificador_sistema="MOPRED-SC-01",
    limiar_alerta=0.80
)

# Dados da passagem suspeita
passagem = {
    "placa": "ABC1234",
    "escore": 0.92,
    "timestampDeteccao": "2025-08-13T00:00:00Z",
    "lat": -27.5954,
    "lon": -48.5480,
    "descricaoArea": "Centro de Florianópolis",
    "modeloInferido": "Civic (Prata)"
}

# Gerar alerta
alerta = gerador.criar_alerta(passagem)
print(gerador.to_json(alerta, indent=2))
```

### 3. Processamento em Lote

```python
# Lista de passagens suspeitas
pares_info = [...]  # Metadados dos pares
scores = [...]      # Scores de suspeição
explicabilidades = [...]  # Explicabilidades SHAP (opcional)

# Gerar alertas em lote
alertas = gerador.processar_batch_alertas(pares_info, scores, explicabilidades)

# Salvar em NDJSON
with open("alertas.ndjson", "w") as f:
    for alerta in alertas:
        f.write(gerador.to_json(alerta, indent=0) + "\n")
```

## ⚙️ Configuração

### Controle via config.json

A geração de alertas pode ser completamente controlada através do arquivo `config.json`:

```json
{
  "gerar_alertas": true,                           // Habilita/desabilita geração
  "limiar_alertas": 0.80,                         // Score mínimo para alertas
  "identificador_sistema_alertas": "MOPRED-SC-01" // ID do sistema nos alertas
}
```

### Parâmetros de Controle

- **`gerar_alertas`** (boolean):
  - `true`: Gera alertas automaticamente durante o processamento
  - `false`: Desabilita completamente a geração de alertas
  - Padrão: `true`

- **`limiar_alertas`** (float 0.0-1.0):
  - Score mínimo para gerar alerta
  - Exemplos: `0.60` (alta sensibilidade), `0.95` (alta precisão)
  - Padrão: `0.80`

- **`identificador_sistema_alertas`** (string):
  - Identificador único do sistema nos alertas
  - Usado para rastreabilidade e organização
  - Padrão: `"MOPRED-SC-01"`

### Cenários de Uso

| Cenário | gerar_alertas | limiar_alertas | Descrição |
|---------|---------------|----------------|-----------|
| **Produção Padrão** | `true` | `0.80` | Configuração balanceada |
| **Alta Precisão** | `true` | `0.95` | Apenas casos muito suspeitos |
| **Alta Sensibilidade** | `true` | `0.60` | Captura mais casos |
| **Desenvolvimento** | `false` | - | Foco em métricas/performance |

### Parâmetros do Gerador

- **`identificador_sistema`**: ID do sistema (ex: "MOPRED-SC-01")
- **`contexto_url`**: URL do contexto JSON-LD
- **`limiar_alerta`**: Score mínimo para gerar alerta (padrão: 0.80)
- **`status_padrao`**: Status dos alertas ("Real", "Teste", "Exercício")
- **`escopo_padrao`**: Escopo dos alertas ("Público", "Restrito", "Privado")

### Classificação Automática por Score

| Score | Severidade | Urgência | Certeza |
|-------|------------|-----------|---------|
| ≥ 0.90 | Alta | Imediata | Provável |
| ≥ 0.80 | Média | Próxima | Possível |
| < 0.80 | Baixa | Rotina | Indeterminado |

## 🔬 Explicabilidade Integrada

### Recursos de Explicabilidade

1. **SHAP Values**: Contribuição de cada feature para a decisão
2. **Feature Importance**: Importância global das características
3. **Fatores de Risco**: Descrições em linguagem natural
4. **Thresholds Dinâmicos**: Interpretação baseada na distribuição

### Exemplo de Explicabilidade

```json
{
  "idModelo": "RF-v2.1.3",
  "metodo": "SHAP",
  "contribuicoes": [
    {
      "feature": "Velocidade estimada (km/h)",
      "valor": 145.2,
      "impacto": 0.31,
      "sinal": "+"
    }
  ],
  "fatoresDeRisco": [
    "Velocidade incompatível com o fluxo da via.",
    "Rota incomum para o dia/horário."
  ]
}
```

## 📊 Integração com Pipeline Temporal

### Fluxo de Geração

1. **Por Janela**: Alertas gerados durante avaliação de cada janela temporal
2. **Consolidação**: Todos os alertas são consolidados em arquivo único
3. **Explicabilidade**: Relatório SHAP final gera alertas com explicação detalhada

### Arquivos de Saída

```
alertas_janela_001.ndjson    # Alertas da janela 1
alertas_janela_002.ndjson    # Alertas da janela 2
...
alertas_consolidados.ndjson  # Todos os alertas das janelas
alertas_gerados.ndjson       # Alertas do relatório SHAP final
```

## 🧪 Teste e Validação

### Executar Testes

```bash
python testar_alertas.py
```

### Validação do Formato

- **JSON-LD válido**: Contexto semântico estruturado
- **UUID únicos**: Identificadores únicos para cada alerta
- **Timestamps ISO8601**: Formato padrão internacional
- **Coordenadas WGS84**: Sistema de coordenadas padrão

## 🔧 Personalização

### Modificar Classificação

Edite a função `_classificar_por_score()` em `alertas.py`:

```python
@staticmethod
def _classificar_por_score(score: float) -> Dict[str, str]:
    # Sua lógica personalizada de classificação
    if score >= 0.95:
        return {"severidade": "Crítica", "urgencia": "Imediata", "certeza": "Observado"}
    # ...
```

### Personalizar Contexto JSON-LD

```python
gerador = GeradorAlertasSimples(
    contexto_url="https://meu-dominio.org/schemas/alerta/v2"
)
```

### Adicionar Recursos Customizados

```python
recursos_extras = [
    {
        "descricaoRecurso": "Captura de Tela",
        "mimeType": "image/jpeg",
        "uri": "/api/v1/recursos/imagem/abc123"
    }
]

alerta = gerador.criar_alerta(passagem, recursos=recursos_extras)
```

## 📈 Métricas e Monitoramento

### Estatísticas Geradas

Durante a execução, o sistema reporta:
- Número de alertas por janela
- Total de alertas consolidados
- Taxa de geração de alertas por score
- Arquivos de saída criados

### Exemplo de Saída

```
🚨 Janela 3: 12 alertas gerados
   📁 Salvos em: alertas_janela_003.ndjson
✅ 45 alertas consolidados em: alertas_consolidados.ndjson
📊 Arquivos de janela: 8 arquivos
```

## 🎓 Benefícios para Pesquisa

1. **Padronização**: Formato consistente conforme especificação da tese
2. **Interoperabilidade**: JSON-LD permite integração semântica
3. **Rastreabilidade**: UUID único e timestamp para auditoria
4. **Explicabilidade**: Transparência nas decisões do modelo
5. **Escalabilidade**: Processamento em lote e por janelas temporais

---

Este sistema representa a evolução completa da solução para incluir alertas padronizados com explicabilidade, mantendo a simplicidade necessária para prototipagem e validação acadêmica.
