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


def carregar_configuracoes() -> Dict[str, Any]:
    """Carrega as configurações do sistema."""
    config_path = "configs/config.json"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config


def verificar_dependencias():
    """Verifica se todos os módulos necessários estão disponíveis."""
    print("🔍 Verificando dependências...")
    
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
    
    print("✅ Todas as dependências verificadas")


def criar_diretorios_necessarios(config: Dict[str, Any]):
    """Cria diretórios necessários para o sistema."""
    print("📁 Criando diretórios necessários...")
    
    diretorios = []
    
    # Pasta de CSVs
    pasta_csvs = config.get("pasta_csvs", "csvs")
    diretorios.append(pasta_csvs)
    
    # Pasta de alertas
    pasta_alertas = config.get("pasta_alertas", "alertas_gerados")
    diretorios.append(pasta_alertas)
    
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"   📂 Criado: {diretorio}")
        else:
            print(f"   ✅ Existe: {diretorio}")


def executar_passo(numero: int, titulo: str, funcao, *args, **kwargs):
    """Executa um passo do pipeline com tratamento de erros."""
    print(f"\n{'='*60}")
    print(f"🔄 PASSO {numero}: {titulo}")
    print(f"{'='*60}")
    
    tempo_inicio = time.time()
    
    try:
        resultado = funcao(*args, **kwargs)
        tempo_fim = time.time()
        duracao = tempo_fim - tempo_inicio
        
        print(f"✅ PASSO {numero} CONCLUÍDO COM SUCESSO")
        print(f"   ⏱️ Duração: {duracao:.1f} segundos")
        
        return resultado
        
    except Exception as e:
        tempo_fim = time.time()
        duracao = tempo_fim - tempo_inicio
        
        print(f"❌ ERRO NO PASSO {numero}")
        print(f"   ⏱️ Duração até o erro: {duracao:.1f} segundos")
        print(f"   🔥 Erro: {str(e)}")
        
        # Imprimir stack trace para debug
        import traceback
        print(f"   📋 Stack trace:")
        traceback.print_exc()
        
        raise


def passo_1_gerar_veiculos():
    """Passo 1: Geração de veículos com clones."""
    print("🚗 Iniciando geração de veículos com clones...")
    
    # Importar e executar o gerador de veículos
    import gerar_veiculos_com_clones
    gerar_veiculos_com_clones.main()
    
    print("🎉 Geração de veículos concluída!")


def passo_2_validacao_modelo(config: Dict[str, Any]):
    """Passo 2: Validação do modelo conceitual e treinamento."""
    print("🧠 Iniciando validação do modelo conceitual...")
    
    # Importar e executar a validação
    import validacao_modelo_conceitual
    validacao_modelo_conceitual.main(config)
    
    print("🎉 Validação do modelo concluída!")


def passo_3_analisar_resultados():
    """Passo 3: Análise dos resultados."""
    print("📊 Iniciando análise dos resultados...")
    
    # Verificar se o arquivo de resultados existe
    config = carregar_configuracoes()
    pasta_csvs = config.get("pasta_csvs", "csvs")
    arquivo_resultados = os.path.join(pasta_csvs, "comparacao_modelos_resultados.csv")
    
    if not os.path.exists(arquivo_resultados):
        raise FileNotFoundError(f"Arquivo de resultados não encontrado: {arquivo_resultados}")
    
    # Importar e executar a análise
    import analisar_resultados
    analisar_resultados.analisar_resultados()
    
    print("🎉 Análise dos resultados concluída!")


def imprimir_resumo_final(config: Dict[str, Any], tempo_total: float):
    """Imprime um resumo final da execução."""
    print(f"\n{'='*60}")
    print(f"🎉 EXECUÇÃO COMPLETA DO SISTEMA MOPRED")
    print(f"{'='*60}")
    
    print(f"⏱️ Tempo total de execução: {tempo_total:.1f} segundos ({tempo_total/60:.1f} minutos)")
    print(f"📅 Data/hora de conclusão: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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
    print("🚀 SISTEMA MOPRED - CICLO COMPLETO DE EXECUÇÃO")
    print("=" * 60)
    print(f"📅 Iniciando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tempo_inicio_total = time.time()
    
    try:
        # Verificações iniciais
        verificar_dependencias()
        config = carregar_configuracoes()
        criar_diretorios_necessarios(config)
        
        print(f"\n📋 Configurações carregadas:")
        print(f"   🚗 Total de veículos: {config.get('total_veiculos', 'N/A'):,}")
        print(f"   🔄 Veículos clonados: {config.get('percentual_veiculos_clonados', 'N/A'):.1%}")
        print(f"   ⏱️ Simulação: {config.get('intervalo_tempo_simulacao_horas', 'N/A')}h")
        print(f"   📡 Cidades: {len(config.get('sensores_por_cidade', {}))}")
        print(f"   🚨 Gerar alertas: {'✅' if config.get('gerar_alertas', False) else '❌'}")
        
        # Executar os 3 passos principais
        executar_passo(1, "GERAÇÃO DE VEÍCULOS COM CLONES", passo_1_gerar_veiculos)
        
        executar_passo(2, "VALIDAÇÃO DO MODELO CONCEITUAL", passo_2_validacao_modelo, config)
        
        executar_passo(3, "ANÁLISE DOS RESULTADOS", passo_3_analisar_resultados)
        
        # Resumo final
        tempo_fim_total = time.time()
        tempo_total = tempo_fim_total - tempo_inicio_total
        
        imprimir_resumo_final(config, tempo_total)
        
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
