# Pasta de Testes - MOPRED

Esta pasta contém todos os arquivos de teste e debug criados durante o desenvolvimento e correções do sistema MOPRED.

## 📁 Estrutura das Pastas

### 🏙️ `correcoes_cidades/`
Arquivos relacionados à correção do mapeamento de coordenadas para cidades nos alertas:

- `debug_cidades.py` - Script de investigação do problema das cidades aparecerem como "N/A"
- `teste_correcao_cidades.py` - Teste da função de mapeamento de coordenadas
- `teste_alertas_cidades.py` - Teste de geração de alertas com cidades corrigidas
- `verificar_correcao_final.py` - Verificação final da correção das cidades

### 🚨 `validacao_alertas/`
Arquivos relacionados à validação e correção dos alertas JSON-LD:

- `testar_alertas.py` - Teste do módulo de alertas JSON-LD principal
- `testar_formatacao_alertas.py` - Teste de formatação correta de alertas
- `teste_alerta_formatacao.ndjson` - Arquivo de exemplo para testes
- `teste_pasta_alertas.py` - Teste do sistema de pasta configurável para alertas
- `validar_pasta_alertas.py` - Validação da pasta de alertas
- `teste_formatacao_json.py` - Teste de formatação JSON dos alertas
- `teste_correcao_shap.py` - Teste de correção dos valores SHAP
- `teste_alertas_corrigidos.py` - Teste de alertas com correções aplicadas
- `validar_correcoes.py` - Validação das correções
- `verificar_correcoes.py` - Verificação das correções

### 🔧 `debug_geral/`
Arquivos de debug geral e outras verificações:

- `debug_processamento.py` - Debug do processamento geral
- `verificar_caracteristicas_clones.py` - Verificação das características dos clones

### 🎭 `demos/`
Arquivos de demonstração e exemplos:

- `demo_controle_alertas.py` - Demonstração do controle de alertas via configuração

### 📂 `teste_alertas_cidades/`
Pasta com resultados de testes de alertas com cidades (se existir)

## 🎯 Histórico de Correções

1. **Problema das Cidades (N/A)**: Resolvido com implementação da função `encontrar_cidade_por_coordenadas`
2. **Formatação JSON**: Corrigido para formato NDJSON apropriado
3. **Erros SHAP**: Corrigido tratamento de arrays numpy
4. **Pasta Configurável**: Implementado sistema de pasta configurável via `config.json`

## 🚀 Como Usar

Para executar qualquer teste, use:
```bash
cd "d:\Workspace\mopred"
D:/Workspace/mopred/venv/Scripts/python.exe testes/[categoria]/[arquivo_teste].py
```

Exemplo:
```bash
D:/Workspace/mopred/venv/Scripts/python.exe testes/correcoes_cidades/verificar_correcao_final.py
```

## 📝 Notas

- Todos os testes foram movidos da raiz do projeto para manter a organização
- Os arquivos principais do sistema (`teste_modelos_temporais.py`, `alertas.py`, etc.) permanecem na raiz
- Esta organização facilita a manutenção e localização dos arquivos de teste
