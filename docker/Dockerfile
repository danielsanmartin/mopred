# MOPRED - Sistema de Detecção de Clonagem Veicular
# Dockerfile Multi-Stage para ambiente de produção e desenvolvimento

# ===== STAGE 1: Base =====
FROM python:3.10-slim as base

# Metadados do projeto
LABEL maintainer="MOPRED Research Team"
LABEL description="Sistema de Detecção de Clonagem Veicular com ML Adaptativo"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MOPRED_HOME=/app
ENV CONFIG_PATH=/app/configs

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR $MOPRED_HOME

# ===== STAGE 2: Dependencies =====
FROM base as dependencies

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===== STAGE 3: Development =====
FROM dependencies as development

# Dependências adicionais para desenvolvimento
RUN pip install --no-cache-dir \
    jupyter==1.0.0 \
    jupyterlab==4.0.0 \
    ipykernel==6.25.0 \
    black==23.7.0 \
    flake8==6.0.0 \
    pytest==7.4.0

# Copiar código fonte completo para desenvolvimento
COPY . .

# Criar diretórios necessários
RUN mkdir -p csvs alertas_gerados testes configs

# Expor porta para Jupyter
EXPOSE 8888

# Comando para desenvolvimento
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--LabApp.token=''"]

# ===== STAGE 4: Production =====
FROM dependencies as production

# Copiar apenas arquivos necessários para produção
COPY main.py .
COPY validacao_modelo_conceitual.py .
COPY gerar_veiculos_com_clones.py .
COPY analisar_resultados.py .
COPY alertas.py .
COPY gerador_veiculos.py .
COPY simulador_streaming_alpr.py .
COPY comparador_modelos.py .
COPY utils.py .
COPY configs/ ./configs/

# Criar diretórios de dados
RUN mkdir -p csvs alertas_gerados

# Configurar usuário não-root para segurança
RUN groupadd -r mopred && useradd -r -g mopred mopred
RUN chown -R mopred:mopred $MOPRED_HOME
USER mopred

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import pandas, numpy, sklearn; print('MOPRED Health OK')" || exit 1

# Comando padrão - executa o ciclo completo
CMD ["python", "main.py"]
