# 🎯 EXEMPLO DE USO - MOPRED Docker

## Quando o Docker estiver instalado e rodando:

### 1. Build das imagens:
```bash
cd docker
.\build.bat  # Windows
# ou
./build.sh   # Linux/Mac
```

### 2. Executar sistema completo:
```bash
docker-compose up
```

### 3. Desenvolvimento com Jupyter:
```bash
docker-compose --profile dev up mopred-dev
# Acesse: http://localhost:8888
```

### 4. Apenas análise:
```bash
docker-compose --profile analysis up mopred-analysis
```

## Estrutura Criada:

✅ docker/Dockerfile - Multi-stage build
✅ docker/docker-compose.yml - Orquestração
✅ docker/.dockerignore - Otimização
✅ docker/build.sh - Build Linux/Mac
✅ docker/build.bat - Build Windows  
✅ docker/README.md - Documentação completa

## Características Implementadas:

🐳 **Multi-stage build** - Imagens otimizadas
🔒 **Segurança** - Usuário não-root
📊 **Monitoramento** - Health checks
🔧 **Desenvolvimento** - Jupyter Lab integrado
📁 **Volumes persistentes** - Dados preservados
🎯 **Profiles** - prod/dev/analysis
📋 **Documentação** - README detalhado

## Status: ✅ PRONTO PARA USO

A solução Docker está completamente implementada na pasta `docker/`!
