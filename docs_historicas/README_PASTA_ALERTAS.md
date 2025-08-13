# 📁 Configuração de Pasta para Alertas

## Visão Geral

O sistema agora suporta a configuração de uma pasta personalizada para salvar todos os arquivos de alertas gerados. Esta funcionalidade permite melhor organização e gerenciamento dos arquivos de saída.

## Como Configurar

### 1. Configuração no `config.json`

Adicione ou modifique o campo `pasta_alertas` no arquivo `config.json`:

```json
{
  "gerar_alertas": true,
  "limiar_alertas": 0.80,
  "identificador_sistema_alertas": "MOPRED-SC-01",
  "pasta_alertas": "alertas_gerados"
}
```

### 2. Configurações Disponíveis

| Campo | Tipo | Padrão | Descrição |
|-------|------|---------|-----------|
| `pasta_alertas` | string | `"alertas_gerados"` | Nome da pasta onde os alertas serão salvos |

### 3. Comportamento do Sistema

- **Criação Automática**: A pasta será criada automaticamente se não existir
- **Caminho Relativo**: A pasta é criada a partir do diretório de execução do script
- **Organização**: Todos os arquivos de alertas são salvos na pasta configurada:
  - `alertas_janela_001.ndjson`, `alertas_janela_002.ndjson`, etc.
  - `alertas_consolidados.ndjson`
  - `alertas_gerados.ndjson`

## Exemplos de Uso

### Configuração Padrão
```json
{
  "pasta_alertas": "alertas_gerados"
}
```
**Resultado**: Alertas salvos em `./alertas_gerados/`

### Configuração por Data
```json
{
  "pasta_alertas": "alertas_2025_08_12"
}
```
**Resultado**: Alertas salvos em `./alertas_2025_08_12/`

### Configuração por Projeto
```json
{
  "pasta_alertas": "resultados/alertas_experimento_01"
}
```
**Resultado**: Alertas salvos em `./resultados/alertas_experimento_01/`

## Arquivos Gerados

### 1. Alertas por Janela
- **Nome**: `alertas_janela_XXX.ndjson` (onde XXX é o número da janela)
- **Formato**: NDJSON (um JSON por linha)
- **Conteúdo**: Alertas específicos de cada janela temporal

### 2. Alertas Consolidados  
- **Nome**: `alertas_consolidados.ndjson`
- **Formato**: NDJSON
- **Conteúdo**: Todos os alertas de todas as janelas em um único arquivo

### 3. Alertas de Análise XAI
- **Nome**: `alertas_gerados.ndjson`
- **Formato**: NDJSON
- **Conteúdo**: Alertas gerados durante análise de explicabilidade SHAP

## Vantagens

✅ **Organização**: Todos os alertas ficam em uma pasta dedicada  
✅ **Flexibilidade**: Pasta configurável via JSON  
✅ **Automação**: Criação automática da pasta  
✅ **Compatibilidade**: Funciona com todos os tipos de alertas  
✅ **Consolidação**: Busca automática na pasta configurada  

## Migração de Arquivos Existentes

Se você já tem arquivos de alertas na raiz, pode movê-los para a nova pasta:

```bash
# Criar pasta (se necessário)
mkdir alertas_gerados

# Mover arquivos existentes
mv alertas_*.ndjson alertas_gerados/
```

## Resolução de Problemas

### Problema: Pasta não é criada
**Solução**: Verificar permissões de escrita no diretório

### Problema: Arquivos não são encontrados na consolidação
**Solução**: Verificar se `pasta_alertas` no config.json está correto

### Problema: Caminho inválido
**Solução**: Usar apenas caracteres válidos para nomes de pasta (evitar `:`, `*`, `?`, etc.)

## Logs do Sistema

O sistema exibe mensagens informativas sobre a pasta:

```
📁 Pasta criada: alertas_gerados
✅ 15 alertas únicos salvos em: alertas_gerados/alertas_janela_003.ndjson
✅ 287 alertas consolidados em: alertas_gerados/alertas_consolidados.ndjson
📁 Pasta de alertas: alertas_gerados
```

---

Para mais informações, consulte a documentação completa em `README_ALERTAS.md`.
