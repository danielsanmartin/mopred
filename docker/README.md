# 🐳 MOPRED Docker

Containerização completa do Sistema MOPRED para facilitar deployment e desenvolvimento.

## 📁 Estrutura

```
docker/
├── Dockerfile              # Multi-stage build (prod + dev)
├── docker-compose.yml      # Orquestração de serviços
├── .dockerignore           # Arquivos ignorados no build
├── build.sh               # Script de build (Linux/Mac)
├── build.bat              # Script de build (Windows)
└── README.md              # Esta documentação
```

## 🚀 Quick Start

### 1. Build das Imagens

**Windows:**
```batch
cd docker
build.bat
```

**Linux/Mac:**
```bash
cd docker
chmod +x build.sh
./build.sh
```

### 2. Execução

**Produção (Ciclo Completo):**
```bash
cd docker
docker-compose up
```

**Desenvolvimento (Jupyter Lab):**
```bash
cd docker
docker-compose --profile dev up mopred-dev
```

**Apenas Análise:**
```bash
cd docker
docker-compose --profile analysis up mopred-analysis
```

## 🎯 Serviços Disponíveis

### 📊 mopred (Produção)
- **Função:** Executa o ciclo completo do sistema
- **Comando:** `python main.py`
- **Volumes:** csvs/, alertas_gerados/, configs/
- **Recursos:** 2-4GB RAM, 1-2 CPUs

### 🛠️ mopred-dev (Desenvolvimento)
- **Função:** Ambiente de desenvolvimento com Jupyter
- **URL:** http://localhost:8888
- **Volumes:** Todo o código fonte montado
- **Profile:** `dev`

### 📈 mopred-analysis (Análise)
- **Função:** Apenas análise de resultados
- **Comando:** `python analisar_resultados.py`
- **Profile:** `analysis`

## 📋 Comandos Úteis

### Build e Execução
```bash
# Build manual
docker build -f docker/Dockerfile -t mopred:latest .

# Executar container diretamente
docker run -v $(pwd)/csvs:/app/csvs -v $(pwd)/alertas_gerados:/app/alertas_gerados mopred:latest

# Modo interativo
docker run -it --rm mopred:latest bash
```

### Gerenciamento
```bash
# Ver logs
docker-compose logs -f mopred

# Parar serviços
docker-compose down

# Remover volumes
docker-compose down -v

# Ver status
docker-compose ps
```

### Debug
```bash
# Entrar no container em execução
docker exec -it mopred-sistema bash

# Health check manual
docker exec mopred-sistema python -c "import pandas, numpy, sklearn; print('OK')"
```

## 🔧 Configuração

### Variáveis de Ambiente
- `PYTHONUNBUFFERED=1` - Output em tempo real
- `CONFIG_PATH=/app/configs` - Caminho das configurações
- `TZ=America/Sao_Paulo` - Fuso horário

### Volumes Persistentes
- `csvs/` - Datasets gerados
- `alertas_gerados/` - Alertas e relatórios
- `configs/` - Arquivos de configuração

### Recursos
- **Memória:** 2-4GB (configurável)
- **CPU:** 1-2 cores (configurável)
- **Disco:** ~2GB para imagem + dados

## 🐛 Troubleshooting

### Problemas Comuns

**1. Erro de memória:**
```bash
# Aumentar limite no docker-compose.yml
memory: 6G
```

**2. Permissões no Linux:**
```bash
sudo chown -R $USER:$USER csvs/ alertas_gerados/
```

**3. Jupyter não acessível:**
```bash
# Verificar porta e firewall
curl http://localhost:8888
```

**4. Container não inicia:**
```bash
# Ver logs detalhados
docker-compose logs mopred
```

## 🔒 Segurança

- ✅ Usuário não-root no container
- ✅ Volumes com permissões adequadas
- ✅ Configs em modo somente leitura
- ✅ Health checks configurados
- ✅ Logs com rotação automática

## 📊 Performance

### Otimizações Implementadas
- Multi-stage build (imagens menores)
- Cache eficiente do pip
- Dependências mínimas em produção
- Volumes nomeados para venv

### Métricas Típicas
- **Build time:** ~3-5 minutos
- **Tamanho da imagem:** ~1.5GB
- **Tempo de inicialização:** ~30 segundos
- **Uso de memória:** 1-3GB durante execução

## 🎉 Pronto!

O sistema MOPRED agora pode ser executado em qualquer ambiente com Docker, garantindo:
- ✅ Reprodutibilidade total
- ✅ Isolamento de dependências  
- ✅ Facilidade de deployment
- ✅ Ambiente de desenvolvimento padronizado
