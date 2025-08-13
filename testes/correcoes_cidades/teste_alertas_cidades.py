#!/usr/bin/env python3
"""
Teste de geração de alertas com correção das cidades
"""

import json
import os
import sys
import os

# Adicionar a raiz do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validacao_modelo_conceitual import *
from simulador_streaming_alpr import SimuladorStreamingALPR
from comparador_modelos import ComparadorModelos

def testar_alertas_com_cidades():
    """Testa a geração de alertas com mapeamento correto de cidades"""
    
    print("🧪 TESTANDO GERAÇÃO DE ALERTAS COM CIDADES CORRIGIDAS...")
    
    # Carregar configuração
    with open("configs/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Configurar para gerar alertas de teste em pasta separada
    config["pasta_alertas"] = "teste_alertas_cidades"
    config["gerar_alertas"] = True
    config["limiar_alertas"] = 0.5  # Limiar mais baixo para gerar mais alertas
    
    # Criar pasta de teste
    os.makedirs("teste_alertas_cidades", exist_ok=True)
    
    try:
        # Simular dados
        print("📊 Inicializando simulador...")
        simulador = SimuladorStreamingALPR("configs/config.json")
        comparador = ComparadorModelos(simulador)
        
        # Executar simulação completa para obter eventos
        print("🎬 Executando simulação...")
        eventos = simulador.executar_simulacao_completa()
        
        if not eventos:
            print("❌ Nenhum evento gerado")
            return
            
        print(f"✅ {len(eventos)} eventos gerados")
        
        # Usar apenas os primeiros eventos para teste rápido
        eventos_teste = eventos[:50]
        
        # Preparar dados para treinar modelo
        print("🤖 Preparando dados para treino...")
        dados_treino = []
        for i, evento in enumerate(eventos_teste):
            if i > 0:  # Criar pares de eventos
                dados_treino.append({
                    'evento1': eventos_teste[i-1],
                    'evento2': evento,
                    'e_suspeito': False  # Para teste simples
                })
                
        X_inicial, y_inicial = comparador.preparar_dados(dados_treino)
        
        # Treinar modelo
        print("🤖 Treinando modelo de teste...")
        modelo_rf = comparador.treinar_modelo(X_inicial, y_inicial)
        
        # Usar eventos existentes como janela de teste
        print("🚨 Preparando janela de teste...")
        eventos_janela = eventos_teste[-20:]  # Usar últimos 20 eventos como janela de teste
        
        # Gerar alertas com correção
        print("✨ Gerando alertas com mapeamento de cidades...")
        alertas = gerar_alertas_janela(modelo_rf, eventos_janela, janela_numero=888, config=config)
        
        print(f"\n📋 RESULTADOS:")
        print(f"   Alertas gerados: {len(alertas)}")
        
        if alertas:
            print(f"\n📍 Exemplos de descrições de área (com cidades corrigidas):")
            for i, alerta in enumerate(alertas[:5]):
                desc_area = alerta.get("area", {}).get("descricao", "N/A")
                coords = alerta.get("area", {}).get("geometria", {}).get("coordenadas", [])
                print(f"   {i+1}. {desc_area}")
                if coords:
                    print(f"      Coords: [{coords[0]:.4f}, {coords[1]:.4f}]")
                    
            # Salvar um alerta de teste
            nome_arquivo = os.path.join(config["pasta_alertas"], "alertas_teste_cidades.ndjson")
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                for alerta in alertas:
                    f.write(json.dumps(alerta, ensure_ascii=False) + "\n")
            
            print(f"\n💾 Alertas salvos em: {nome_arquivo}")
            print("✅ Teste concluído! Verifique se as cidades aparecem corretamente.")
        else:
            print("⚠️ Nenhum alerta foi gerado (pode ser devido ao limiar ou dados)")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_alertas_com_cidades()
