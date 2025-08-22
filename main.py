#!/usr/bin/env python3
"""
Sistema MOPRED - Ciclo Completo de Execução
==========================================

Este script executa o ciclo completo do sistema MOPRED:
1. Geração de veículos com clones
2. Validação do modelo conceitual e treinamento
3. Análise dos resultados

Uso:
    python main.py

Autor: Sistema MOPRED
Data: 2025
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any
import argparse
import logging
from pathlib import Path
import random
import numpy as np

# Configuração de encoding para Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)


def carregar_configuracoes(config_path: str = "configs/config.json") -> Dict[str, Any]:
    """Carrega as configurações do sistema."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def setup_logger(log_dir: str = "logs") -> str:
    """Configura logging em arquivo e console. Retorna caminho do arquivo de log."""
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"mopred_run_{ts}.log")

    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logging.info("Logger inicializado.")
    return log_path

def _fmt_int(v):
    return f"{v:,}" if isinstance(v, int) else "N/A"

def _fmt_pct(v):
    return f"{v:.1%}" if isinstance(v, (int, float)) else "N/A"


def verificar_dependencias():
    """Verifica se todos os módulos necessários estão disponíveis."""
    logging.info("Verificando dependências...")
    
    modulos_necessarios = [
        'gerador_veiculos',
        'gerar_veiculos_com_clones', 
        'validacao_modelo_conceitual',
        'analisar_resultados'
    ]
    
    for modulo in modulos_necessarios:
        arquivo = f"{modulo}.py"
        if not os.path.exists(arquivo):
            raise FileNotFoundError(f"Módulo necessário não encontrado: {arquivo}")
    logging.info("Dependências OK.")


def criar_diretorios_necessarios(config: Dict[str, Any]):
    """Cria diretórios necessários para o sistema."""
    logging.info("Criando diretórios necessários...")
    
    diretorios = []
    
    # Pasta de CSVs
    pasta_csvs = config.get("pasta_csvs", "csvs")
    diretorios.append(pasta_csvs)
    
    # Pasta de alertas
    pasta_alertas = config.get("pasta_alertas", "alertas_gerados")
    diretorios.append(pasta_alertas)
    
    for diretorio in diretorios:
        Path(diretorio).mkdir(parents=True, exist_ok=True)
        logging.info(f"Diretório OK: {diretorio}")


def _set_global_seed(seed: int | None):
    """Fixa fontes de aleatoriedade para reprodutibilidade."""
    if seed is None:
        return
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    logging.info(f"Seed global fixada: {seed}")


def executar_passo(numero: int, titulo: str, funcao, *args, **kwargs):
    """Executa um passo do pipeline com tratamento de erros."""
    print(f"\n{'='*60}")
    print(f"🔄 PASSO {numero}: {titulo}")
    print(f"{'='*60}")
    
    tempo_inicio = time.time()
    
    try:
        logging.info(f"Iniciando PASSO {numero}: {titulo}")
        resultado = funcao(*args, **kwargs)
        tempo_fim = time.time()
        duracao = tempo_fim - tempo_inicio
        
        print(f"✅ PASSO {numero} CONCLUÍDO COM SUCESSO")
        print(f"   ⏱️ Duração: {duracao:.1f} segundos")
        logging.info(f"PASSO {numero} concluído em {duracao:.1f}s")
        
        return resultado
        
    except Exception as e:
        tempo_fim = time.time()
        duracao = tempo_fim - tempo_inicio
        
        print(f"❌ ERRO NO PASSO {numero}")
        print(f"   ⏱️ Duração até o erro: {duracao:.1f} segundos")
        print(f"   🔥 Erro: {str(e)}")
        logging.exception(f"Erro no PASSO {numero} após {duracao:.1f}s: {e}")
        
        # Imprimir stack trace para debug
        import traceback
        print(f"   📋 Stack trace:")
        traceback.print_exc()
        
        raise


def passo_1_gerar_veiculos(config: Dict[str, Any]):
    """Passo 1: Geração de veículos com clones."""
    print("🚗 Iniciando geração de veículos com clones...")
    
    # Importar e executar o gerador de veículos
    import gerar_veiculos_com_clones
    # Garantir que o gerador use a mesma config deste cenário
    cfg_path = config.get("_config_path", "configs/config.json")
    gerar_veiculos_com_clones.main(config_path=cfg_path)
    
    print("🎉 Geração de veículos concluída!")


def passo_2_validacao_modelo(config: Dict[str, Any]):
    """Passo 2: Validação do modelo conceitual e treinamento."""
    print("🧠 Iniciando validação do modelo conceitual...")
    
    # Importar e executar a validação
    import validacao_modelo_conceitual
    validacao_modelo_conceitual.main(config)

    # Garantir que o CSV de resultados exista para o cenário atual
    try:
        pasta_csvs = config.get("pasta_csvs", "csvs")
        os.makedirs(pasta_csvs, exist_ok=True)
        csv_path = os.path.join(pasta_csvs, "comparacao_modelos_resultados.csv")
        if not os.path.exists(csv_path):
            # Criar CSV vazio com cabeçalho padrão
            header = [
                'janela', 'accuracy', 'precision', 'recall', 'f1', 'auprc', 'brier',
                'n_amostras', 'n_suspeitos', 'tipo', 'y_true', 'y_score',
                'num_infracoes', 'semelhanca'
            ]
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(','.join(header) + "\n")
            print(f"⚠️ CSV de resultados não gerado pela validação; criado arquivo vazio: {csv_path}")
    except Exception as _e:
        # Não interromper o fluxo por falha ao criar um CSV vazio
        pass
    
    print("🎉 Validação do modelo concluída!")


def passo_3_analisar_resultados():
    """Passo 3: Análise dos resultados."""
    print("📊 Iniciando análise dos resultados...")
    
    # Verificar se o arquivo de resultados existe
    cfg_env = os.environ.get("MOPRED_CONFIG", "configs/config.json")
    config = carregar_configuracoes(cfg_env)
    pasta_csvs = config.get("pasta_csvs", "csvs")
    arquivo_resultados = os.path.join(pasta_csvs, "comparacao_modelos_resultados.csv")
    
    if not os.path.exists(arquivo_resultados):
        raise FileNotFoundError(f"Arquivo de resultados não encontrado: {arquivo_resultados}")
    
    # Importar e executar a análise
    import analisar_resultados
    analisar_resultados.analisar_resultados()
    
    print("🎉 Análise dos resultados concluída!")


def imprimir_resumo_final(config: Dict[str, Any], tempo_total: float, log_path: str | None = None):
    """Imprime um resumo final da execução."""
    print(f"\n{'='*60}")
    print(f"🎉 EXECUÇÃO COMPLETA DO SISTEMA MOPRED")
    print(f"{'='*60}")
    
    print(f"⏱️ Tempo total de execução: {tempo_total:.1f} segundos ({tempo_total/60:.1f} minutos)")
    print(f"📅 Data/hora de conclusão: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if log_path:
        print(f"🗒️ Log: {log_path}")
    
    print(f"\n📁 Arquivos gerados:")
    
    # Verificar arquivos gerados
    pasta_csvs = config.get("pasta_csvs", "csvs")
    pasta_alertas = config.get("pasta_alertas", "alertas_gerados")
    
    arquivos_esperados = [
        (os.path.join(pasta_csvs, "veiculos_gerados_com_clones.csv"), "🚗 Dataset de veículos"),
        (os.path.join(pasta_csvs, "passagens_streaming.csv"), "📡 Eventos de passagem"),
        (os.path.join(pasta_csvs, "comparacao_modelos_resultados.csv"), "📊 Resultados da comparação"),
        (os.path.join(pasta_alertas, "alertas_consolidados.ndjson"), "🚨 Alertas consolidados")
    ]
    
    for arquivo, descricao in arquivos_esperados:
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)
            tamanho_mb = tamanho / (1024 * 1024)
            print(f"   ✅ {descricao}: {arquivo} ({tamanho_mb:.1f} MB)")
        else:
            print(f"   ⚠️ {descricao}: {arquivo} (não encontrado)")
    
    print(f"\n💡 Próximos passos sugeridos:")
    print(f"   • Revisar os alertas gerados em: {pasta_alertas}/")
    print(f"   • Analisar as métricas em: {pasta_csvs}/comparacao_modelos_resultados.csv")
    print(f"   • Executar análises adicionais conforme necessário")
    
    print(f"\n🏆 Sistema MOPRED executado com sucesso!")


def main():
    """Função principal - executa o ciclo completo do sistema MOPRED."""
    # argparse: seleção de config e passos
    parser = argparse.ArgumentParser(description="Executa o ciclo completo do MOPRED.")
    parser.add_argument("--config", default="configs/config.json", help="Caminho para o arquivo de configuração.")
    parser.add_argument("--steps", default="1,2,3", help="Quais passos executar. Ex.: 1,2,3 ou 2,3")
    args = parser.parse_args()

    # Carregar config cedo para aplicar PYTHONHASHSEED antes de qualquer inicialização
    try:
        config = carregar_configuracoes(args.config)
    except Exception:
        # Em caso de erro de config, ainda imprimir banner básico antes de sair
        print("🚀 SISTEMA MOPRED - CICLO COMPLETO DE EXECUÇÃO")
        print("=" * 60)
        raise

    # Nota: PYTHONHASHSEED só é aplicado no início do interpretador.
    # Em alguns ambientes (Windows/VS Code) uma reexecução do processo pode falhar.
    seed_cfg = config.get("seed", 42)
    phs = os.environ.get("PYTHONHASHSEED")
    if phs is None or phs != str(seed_cfg):
        print(
            f"INFO: Aviso: PYTHONHASHSEED atual é '{phs}'. Para determinismo máximo, execute com PYTHONHASHSEED={seed_cfg} no ambiente."
        )

    # Tornar o caminho da config acessível a outros módulos
    try:
        config["_config_path"] = args.config
    except Exception:
        pass
    os.environ["MOPRED_CONFIG"] = args.config

    print("🚀 SISTEMA MOPRED - CICLO COMPLETO DE EXECUÇÃO")
    print("=" * 60)
    print(f"📅 Iniciando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_path = setup_logger()

    tempo_inicio_total = time.time()

    try:
        # Verificações iniciais
        verificar_dependencias()
        # config já carregada; Fixar seed global (random, numpy) o mais cedo possível
        _set_global_seed(seed_cfg)
        criar_diretorios_necessarios(config)
        
        print(f"\n📋 Configurações carregadas:")
        print(f"   🚗 Total de veículos: {_fmt_int(config.get('total_veiculos'))}")
        print(f"   🔄 Veículos clonados: {_fmt_pct(config.get('percentual_veiculos_clonados'))}")
        sim_horas = config.get('intervalo_tempo_simulacao_horas')
        print(f"   ⏱️ Simulação: {sim_horas if isinstance(sim_horas,(int,float)) else 'N/A'}h")
        print(f"   📡 Cidades: {len(config.get('sensores_por_cidade', {}))}")
        print(f"   🚨 Gerar alertas: {'✅' if config.get('gerar_alertas', False) else '❌'}")
        protocolo = config.get('protocolo_avaliacao', 'prequential')
        print(f"   🧪 Protocolo de avaliação: {protocolo}")
        seed_info = config.get('seed', None)
        if seed_info is not None:
            print(f"   🎲 Seed: {seed_info}")
        # Executar passos conforme seleção
        steps = {s.strip() for s in str(args.steps).split(',') if s.strip()}
        if "1" in steps:
            executar_passo(1, "GERAÇÃO DE VEÍCULOS COM CLONES", passo_1_gerar_veiculos, config)
        if "2" in steps:
            executar_passo(2, "VALIDAÇÃO DO MODELO CONCEITUAL", passo_2_validacao_modelo, config)
        if "3" in steps:
            executar_passo(3, "ANÁLISE DOS RESULTADOS", passo_3_analisar_resultados)

        # Resumo final
        tempo_fim_total = time.time()
        tempo_total = tempo_fim_total - tempo_inicio_total

        imprimir_resumo_final(config, tempo_total, log_path=log_path)
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Execução interrompida pelo usuário")
        sys.exit(1)
        
    except Exception as e:
        tempo_fim_total = time.time()
        tempo_total = tempo_fim_total - tempo_inicio_total
        
        print(f"\n❌ ERRO FATAL NA EXECUÇÃO")
        print(f"⏱️ Tempo até o erro: {tempo_total:.1f} segundos")
        print(f"🔥 Erro: {str(e)}")
        
        import traceback
        print(f"\n📋 Stack trace completo:")
        traceback.print_exc()
        
        sys.exit(1)


if __name__ == "__main__":
    main()
