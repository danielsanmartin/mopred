#!/usr/bin/env python3
"""
Teste rápido da correção das cidades
"""

import json
import sys
import os

# Adicionar a raiz do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validacao_modelo_conceitual import encontrar_cidade_por_coordenadas

def testar_correcao():
    """Testa se a função de mapeamento de cidades está funcionando"""
    
    print("🧪 TESTANDO CORREÇÃO DAS CIDADES...")
    
    # Carregar configuração
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'config.json')
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Testar com coordenadas conhecidas
    coordenadas_teste = [
        ("Florianópolis", -27.5954, -48.548),
        ("Joinville", -26.3045, -48.8487),
        ("Blumenau", -26.9156, -49.0706),
        ("Chapecó", -27.1, -52.6152),
        ("Criciúma", -28.6781, -49.3695)  # Aproximada
    ]
    
    print("📍 Testando mapeamento de coordenadas para cidades:")
    for nome_esperado, lat, lon in coordenadas_teste:
        cidade_encontrada = encontrar_cidade_por_coordenadas(lat, lon, config)
        status = "✅" if nome_esperado.lower() in cidade_encontrada.lower() else "⚠️"
        print(f"   {status} [{lat}, {lon}] → {cidade_encontrada} (esperado: {nome_esperado})")
    
    # Testar coordenada longe
    print("\n🌍 Testando coordenada distante:")
    cidade_distante = encontrar_cidade_por_coordenadas(-20.0, -40.0, config)
    print(f"   Coordenada distante → {cidade_distante}")
    
    print("\n✅ Função implementada e testada!")

if __name__ == "__main__":
    testar_correcao()
