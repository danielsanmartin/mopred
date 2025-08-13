# Configuração do Git - MOPRED

## 📋 Resumo da Configuração do .gitignore

### 🎯 Objetivo
Ignorar o conteúdo das pastas `csvs/` e `alertas_gerados/` mantendo as pastas no repositório para garantir que a estrutura do projeto seja preservada.

### 📁 Pastas Ignoradas (conteúdo)
- **`csvs/*`** - Todos os arquivos CSV gerados automaticamente
- **`alertas_gerados/*`** - Todos os arquivos JSON-LD de alertas gerados

### 📌 Pastas Mantidas (estrutura)
- **`csvs/.gitkeep`** - Mantém a pasta csvs no repositório
- **`alertas_gerados/.gitkeep`** - Mantém a pasta alertas_gerados no repositório

## 🔧 Configuração Implementada

### .gitignore Atualizado
```ignore
# Arquivos de dados gerados automaticamente
/comparacao_modelos_resultados.csv
/veiculos_gerados_sem_infracao.csv

# Conteúdo das pastas de dados (manter as pastas, ignorar arquivos)
csvs/*
!csvs/.gitkeep
alertas_gerados/*
!alertas_gerados/.gitkeep

# Ambiente virtual Python
/venv
venv/

# Cache Python
/__pycache__
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Arquivos temporários
*.tmp
*.temp
*.log

# Arquivos do sistema
.DS_Store
Thumbs.db

# Arquivos de IDE
.vscode/
.idea/
*.swp
*.swo

# Arquivos de backup
*.bak
*.backup
*~
```

### Arquivos .gitkeep Criados
- **`csvs/.gitkeep`** - Documenta a finalidade da pasta csvs
- **`alertas_gerados/.gitkeep`** - Documenta a finalidade da pasta alertas

## ✅ Validação

### Arquivos Ignorados (✅ Funcionando)
```bash
$ git check-ignore csvs/comparacao_modelos_resultados.csv
csvs/comparacao_modelos_resultados.csv

$ git check-ignore alertas_gerados/alertas_consolidados.ndjson  
alertas_gerados/alertas_consolidados.ndjson
```

### Arquivos Incluídos (✅ Funcionando)
```bash
$ git check-ignore csvs/.gitkeep
# (sem output - arquivo NÃO ignorado)

$ git check-ignore alertas_gerados/.gitkeep
# (sem output - arquivo NÃO ignorado)
```

## 🎯 Benefícios Alcançados

1. **📁 Estrutura Preservada**: Pastas importantes mantidas no repositório
2. **🚫 Dados Ignorados**: Arquivos gerados automaticamente não versionados
3. **📝 Documentação**: Arquivos .gitkeep documentam a finalidade das pastas
4. **🧹 Repositório Limpo**: Apenas código e configuração versionados
5. **⚙️ Flexibilidade**: Sistema funciona mesmo com pastas inicialmente vazias

## 🚀 Resultado Final

Agora o repositório Git:
- ✅ **Versiona** a estrutura de pastas (csvs/, alertas_gerados/)
- ✅ **Ignora** o conteúdo gerado automaticamente
- ✅ **Mantém** arquivos .gitkeep para documentação
- ✅ **Preserva** a funcionalidade do sistema
- ✅ **Otimiza** o tamanho do repositório

**O sistema está configurado para trabalhar corretamente tanto com repositórios novos quanto com dados já gerados!**
