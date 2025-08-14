#!/bin/bash
# ======================================================
# MOPRED - Script de Build para Linux/Mac
# ======================================================

set -e  # Parar em caso de erro

echo ""
echo "================================================"
echo "🐳 MOPRED Docker Build Script"
echo "================================================"
echo ""

# Verificar se Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado! Instale o Docker primeiro."
    exit 1
fi

echo "✅ Docker detectado: $(docker --version)"
echo ""

# Navegar para o diretório do projeto
cd "$(dirname "$0")/.."

echo "📁 Diretório atual: $(pwd)"
echo ""

echo "🔨 Building imagem de produção..."
docker build -f docker/Dockerfile --target production -t mopred:latest .

echo "🔨 Building imagem de desenvolvimento..."
docker build -f docker/Dockerfile --target development -t mopred:dev .

echo ""
echo "✅ Build concluído com sucesso!"
echo ""
echo "📋 Comandos disponíveis:"
echo ""
echo "🚀 Executar produção:"
echo "   cd docker && docker-compose up"
echo ""
echo "🛠️ Executar desenvolvimento:"
echo "   cd docker && docker-compose --profile dev up mopred-dev"
echo ""
echo "📊 Executar apenas análise:"
echo "   cd docker && docker-compose --profile analysis up mopred-analysis"
echo ""
echo "🔍 Ver imagens criadas:"
echo "   docker images mopred"
echo ""

echo "🎉 Pronto para usar!"
