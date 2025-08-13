#!/usr/bin/env python3
"""
Investigação do problema das cidades nos alertas
"""

import json
import pandas as pd
import sys
import os

# Adicionar a raiz do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def investigar_problema_cidades():
    """Investiga por que as cidades aparecem como N/A nos alertas."""
    
    print("🔍 INVESTIGANDO PROBLEMA DAS CIDADES...")
    
    # 1. Verificar configuração
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'config.json')
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    cidades_config = config.get("lat_lon_por_cidade", {})
    print(f"\n📍 Cidades configuradas: {len(cidades_config)} cidades")
    for cidade, coords in list(cidades_config.items())[:5]:
        print(f"   - {cidade}: {coords}")
    print("   ...")
    
    # 2. Testar função de mapeamento
    def encontrar_cidade_por_coordenadas(lat, lon, config):
        """Encontra a cidade mais próxima baseada nas coordenadas"""
        cidades_config = config.get("lat_lon_por_cidade", {})
        raio_max = 1.0  # Raio mais amplo para teste
        
        cidade_mais_proxima = None
        menor_distancia = float('inf')
        
        for cidade, (cidade_lat, cidade_lon) in cidades_config.items():
            # Distância euclidiana simples
            distancia = ((lat - cidade_lat)**2 + (lon - cidade_lon)**2)**0.5
            if distancia < menor_distancia:
                menor_distancia = distancia
                cidade_mais_proxima = cidade
        
        # Se está dentro do raio, retorna a cidade; senão, "Região de [cidade mais próxima]"
        if menor_distancia <= raio_max:
            return cidade_mais_proxima
        else:
            return f"Região de {cidade_mais_proxima}" if cidade_mais_proxima else "Região Desconhecida"
    
    # 3. Testar com coordenadas dos alertas existentes
    print(f"\n🧪 Testando mapeamento com coordenadas dos alertas...")
    
    # Ler um alerta existente para pegar coordenadas reais
    try:
        alerta_path = os.path.join(os.path.dirname(__file__), '..', '..', 'alertas_gerados', 'alertas_janela_005.ndjson')
        with open(alerta_path, "r", encoding="utf-8") as f:
            primeira_linha = f.readline().strip()
            alerta = json.loads(primeira_linha)
            
        coords = alerta["area"]["geometria"]["coordenadas"]
        lat, lon = coords[0], coords[1]  # Note: pode estar como [lon, lat] ou [lat, lon]
        
        print(f"Coordenadas do alerta: [{lat}, {lon}]")
        
        # Testar ambas as ordenações
        cidade1 = encontrar_cidade_por_coordenadas(lat, lon, config)
        cidade2 = encontrar_cidade_por_coordenadas(lon, lat, config)  # Invertido
        
        print(f"Interpretação 1 (lat={lat}, lon={lon}): {cidade1}")
        print(f"Interpretação 2 (lat={lon}, lon={lat}): {cidade2}")
        
        # Verificar qual faz mais sentido
        cidades_sc = list(cidades_config.keys())
        if cidade1 in cidades_sc:
            print(f"✅ Coordenadas corretas: [{lat}, {lon}] → {cidade1}")
        elif cidade2 in cidades_sc:
            print(f"✅ Coordenadas corretas (invertidas): [{lon}, {lat}] → {cidade2}")
        else:
            print(f"⚠️ Nenhuma interpretação encontrou cidade exata")
            
            # Encontrar cidade mais próxima com distância
            menor_dist = float('inf')
            cidade_proxima = None
            for cidade, (c_lat, c_lon) in cidades_config.items():
                dist1 = ((lat - c_lat)**2 + (lon - c_lon)**2)**0.5
                dist2 = ((lon - c_lat)**2 + (lat - c_lon)**2)**0.5
                dist_min = min(dist1, dist2)
                if dist_min < menor_dist:
                    menor_dist = dist_min
                    cidade_proxima = cidade
            
            print(f"   Cidade mais próxima: {cidade_proxima} (distância: {menor_dist:.3f})")
            
    except Exception as e:
        print(f"❌ Erro ao ler alerta: {e}")
    
    # 4. Testar com coordenadas conhecidas
    print(f"\n📍 Testando com coordenadas conhecidas de SC...")
    
    coordenadas_teste = [
        ("Florianópolis", -27.5954, -48.5480),
        ("Joinville", -26.3045, -48.8487),
        ("Blumenau", -26.9156, -49.0706),
        ("Chapecó", -27.1000, -52.6152)
    ]
    
    for nome, lat, lon in coordenadas_teste:
        cidade_encontrada = encontrar_cidade_por_coordenadas(lat, lon, config)
        print(f"   {nome} [{lat}, {lon}] → {cidade_encontrada}")

if __name__ == "__main__":
    investigar_problema_cidades()
