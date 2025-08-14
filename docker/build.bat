@echo off
REM ======================================================
REM MOPRED - Script de Build para Windows
REM ======================================================

echo.
echo ================================================
echo 🐳 MOPRED Docker Build Script
echo ================================================
echo.

REM Verificar se Docker está disponível
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker não encontrado! Instale o Docker Desktop primeiro.
    pause
    exit /b 1
)

echo ✅ Docker detectado
echo.

REM Navegar para o diretório do projeto
cd /d "%~dp0\.."

echo 📁 Diretório atual: %CD%
echo.

echo 🔨 Building imagem de produção...
docker build -f docker/Dockerfile --target production -t mopred:latest .
if %ERRORLEVEL% neq 0 (
    echo ❌ Erro no build da imagem de produção
    pause
    exit /b 1
)

echo 🔨 Building imagem de desenvolvimento...
docker build -f docker/Dockerfile --target development -t mopred:dev .
if %ERRORLEVEL% neq 0 (
    echo ❌ Erro no build da imagem de desenvolvimento
    pause
    exit /b 1
)

echo.
echo ✅ Build concluído com sucesso!
echo.
echo 📋 Comandos disponíveis:
echo.
echo 🚀 Executar produção:
echo    cd docker ^&^& docker-compose up
echo.
echo 🛠️ Executar desenvolvimento:
echo    cd docker ^&^& docker-compose --profile dev up mopred-dev
echo.
echo 📊 Executar apenas análise:
echo    cd docker ^&^& docker-compose --profile analysis up mopred-analysis
echo.
echo 🔍 Ver imagens criadas:
echo    docker images mopred
echo.

pause
