#!/usr/bin/env python3
"""
Teste de regeneração de um arquivo de alertas com formatação correta.
"""

import json
import pandas as pd
import sys
import os

# Adicionar a raiz do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validacao_modelo_conceitual import gerar_alertas_janela

def gerar_teste_alertas():
    """Gera um teste simples de alertas com dados simulados."""
    
    print("🧪 Gerando teste de alertas com formatação correta...")
    
    # Carrega configuração
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Configura para gerar alertas com limiar baixo para ter alguns resultados
    config['gerar_alertas'] = True
    config['limiar_alertas'] = 0.7  # Limiar mais baixo para gerar alertas
    
    # Cria dados simulados simples já como dicionários
    eventos_teste = []
    
    # Simula alguns eventos suspeitos já no formato esperado
    for i in range(10):
        evento = {
            'placa': f'ABC{1000+i}',
            'lat': -27.5969 + (i * 0.001),  # Florianópolis com variação
            'lon': -48.5495 + (i * 0.001),
            'timestamp': 1640995200000 + (i * 3600000),  # 1h de diferença
            'cam': f'CAM_{i%3}',
            'é_clone': i % 3 == 0,  # Cada terceiro é clone
            'num_infracoes': i % 2
        }
        
        # Cria um objeto com método to_dict()
        class EventoSimples:
            def __init__(self, dados):
                self.dados = dados
            def to_dict(self):
                return self.dados
                
        eventos_teste.append(EventoSimples(evento))
    
    print(f"📊 Eventos de teste criados: {len(eventos_teste)}")
    
    try:
        # Cria um modelo simples para teste
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        
        # Modelo fictício treinado
        modelo_rf = RandomForestClassifier(n_estimators=10, random_state=42)
        
        # Dados de treino fictícios para que o modelo tenha feature_importances_
        X_train = np.random.rand(20, 6)  # 6 features padrão
        y_train = np.random.randint(0, 2, 20)
        modelo_rf.fit(X_train, y_train)
        
        # Gera alertas para teste
        alertas = gerar_alertas_janela(
            modelo_rf=modelo_rf,
            eventos_janela=eventos_teste,
            janela_numero=999,  # Número de teste
            limiar_alerta=config['limiar_alertas'],
            config=config
        )
        
        print(f"✅ Geração concluída!")
        print(f"📋 Alertas gerados: {len(alertas) if alertas else 0}")
        
        # Verifica se arquivo foi criado corretamente
        arquivo_teste = "alertas_janela_999.ndjson"
        try:
            with open(arquivo_teste, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            print(f"📁 Arquivo criado com {len(linhas)} linhas")
            
            if linhas:
                # Testa se primeira linha é JSON válido
                try:
                    primeiro_alerta = json.loads(linhas[0].strip())
                    print("✅ Formatação JSON correta!")
                    print(f"  - Placa: {primeiro_alerta['info']['parametrosPreditivos'][0]['valor']}")
                    print(f"  - Probabilidade: {primeiro_alerta['info']['probabilidade']}")
                    print(f"  - Tipo explicação: {primeiro_alerta['info']['explicabilidade']['metodo']}")
                except json.JSONDecodeError as e:
                    print(f"❌ Erro de formatação JSON: {e}")
            else:
                print("ℹ️ Arquivo vazio - normal se limiar muito alto")
                
        except FileNotFoundError:
            print("ℹ️ Arquivo de teste não criado")
            
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    gerar_teste_alertas()
