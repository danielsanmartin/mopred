#!/usr/bin/env python3
"""
Teste das correções implementadas na geração de alertas.
"""

import json
from simulador_streaming_alpr import SimuladorStreamingALPR
import sys
import os

# Adicionar a raiz do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from validacao_modelo_conceitual import gerar_alertas_janela
import os

def teste_alertas_corrigidos():
    """Testa as correções implementadas."""
    
    # Carrega configuração
    with open('configs/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Força geração de alertas com limiar alto para reduzir volume
    config['gerar_alertas'] = True
    config['limiar_alertas'] = 0.90  # Limiar muito alto para poucos alertas
    
    print("🧪 Testando correções na geração de alertas...")
    print(f"⚙️ Limiar configurado: {config['limiar_alertas']}")
    
    # Cria simulador e carrega veículos
    simulador = SimuladorStreamingALPR()
    simulador.carregar_veiculos('veiculos_gerados_com_clones.csv')
    
    print(f"📊 Dados carregados: {len(simulador.veiculos)} veículos")
    
    # Gera eventos de teste usando streaming
    eventos_teste = []
    contador = 0
    
    for evento in simulador.streaming_batch_completo():
        eventos_teste.append(evento.to_dict())
        contador += 1
        if contador >= 50:  # Apenas 50 eventos para teste
            break
    
    print(f"🎯 Eventos gerados: {len(eventos_teste)}")
    
    # Remove arquivo de teste anterior se existir
    arquivo_teste = "alertas_janela_999.ndjson"
    if os.path.exists(arquivo_teste):
        os.remove(arquivo_teste)
    
    # Testa uma janela
    try:
        alertas = gerar_alertas_janela(
            eventos_teste,  # Todos os eventos de teste
            janela_numero=999,
            config=config
        )
        
        print(f"✅ Teste concluído!")
        print(f"📋 Alertas gerados: {len(alertas) if alertas else 0}")
        
        # Verifica se arquivo foi criado
        if os.path.exists(arquivo_teste):
            with open(arquivo_teste, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            print(f"📁 Arquivo criado com {len(linhas)} linhas")
            
            # Mostra um exemplo se houver alertas
            if linhas:
                print("\n📝 Exemplo de alerta gerado:")
                primeiro_alerta = json.loads(linhas[0])
                print(f"  - Placa: {primeiro_alerta['info']['parametrosPreditivos'][0]['valor']}")
                print(f"  - Probabilidade: {primeiro_alerta['info']['probabilidade']}")
                print(f"  - Explicabilidade: {primeiro_alerta['info']['explicabilidade']['metodo']}")
                print(f"  - Coordenadas: {primeiro_alerta['area']['geometria']['coordenadas']}")
        else:
            print("ℹ️ Nenhum arquivo de alertas criado (normal se não há alertas acima do limiar)")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_alertas_corrigidos()
