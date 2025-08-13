"""
Script para debugar a função de processamento e entender por que as features 
de similaridade retornam 1.0 mesmo quando devem ser diferentes.
"""

import pandas as pd
from simulador_streaming_alpr import SimuladorStreamingALPR

def debug_processamento():
    """Debug detalhado do processamento de placas."""
    print("🔧 DEBUG DO PROCESSAMENTO DE PLACAS")
    print("=" * 60)
    
    # Inicializar simulador
    simulador = SimuladorStreamingALPR("config.json")
    eventos = simulador.executar_simulacao_completa()
    
    # Converter para DataFrame
    eventos_dict = [evento.to_dict() for evento in eventos]
    df_eventos = pd.DataFrame(eventos_dict)
    
    # Pegar uma placa clonada específica
    clonados = df_eventos[df_eventos['is_clonado'] == True]
    placas_clonadas = clonados['placa'].value_counts()
    
    # Escolher a primeira placa com múltiplos eventos
    placa_teste = placas_clonadas.index[0]
    eventos_placa = df_eventos[df_eventos['placa'] == placa_teste].sort_values('timestamp')
    
    print(f"📍 Analisando placa: {placa_teste}")
    print(f"📊 Total de eventos: {len(eventos_placa)}")
    
    print("\n🔍 DETALHES DOS EVENTOS:")
    for idx, evento in eventos_placa.iterrows():
        print(f"  Evento {idx}:")
        print(f"    Timestamp: {evento['timestamp']}")
        print(f"    Câmera: {evento['cam']}")
        print(f"    Marca: {evento['marca']}")
        print(f"    Modelo: {evento['modelo']}")
        print(f"    Tipo: {evento['tipo']}")
        print(f"    Cor: {evento['cor']}")
        print()
    
    print("🔧 SIMULANDO PROCESSAMENTO MANUAL:")
    
    # Simular o processamento manual
    for i in range(len(eventos_placa) - 1):
        evento1 = eventos_placa.iloc[i]
        evento2 = eventos_placa.iloc[i + 1]
        
        print(f"\n🔍 Par {i+1}-{i+2}:")
        print(f"  Evento1: {evento1['marca']} {evento1['modelo']} ({evento1['tipo']}) {evento1['cor']}")
        print(f"  Evento2: {evento2['marca']} {evento2['modelo']} ({evento2['tipo']}) {evento2['cor']}")
        
        # Verificar se câmeras são diferentes
        if evento1['cam'] == evento2['cam']:
            print("  ⚠️ MESMO SENSOR - Par será ignorado")
            continue
        
        # Calcular características de similaridade
        marca_modelo_igual = 1.0 if (evento1.get('marca') == evento2.get('marca') and 
                                     evento1.get('modelo') == evento2.get('modelo')) else 0.0
        tipo_igual = 1.0 if evento1.get('tipo') == evento2.get('tipo') else 0.0
        cor_igual = 1.0 if evento1.get('cor') == evento2.get('cor') else 0.0
        
        print(f"  🔧 Características calculadas:")
        print(f"    marca_modelo_igual: {marca_modelo_igual}")
        print(f"    tipo_igual: {tipo_igual}")
        print(f"    cor_igual: {cor_igual}")
        
        if marca_modelo_igual == 0.0:
            print("  ⚠️ MARCA/MODELO DIFERENTES DETECTADOS!")
        if tipo_igual == 0.0:
            print("  ⚠️ TIPO DIFERENTE DETECTADO!")
        if cor_igual == 0.0:
            print("  ⚠️ COR DIFERENTE DETECTADA!")

if __name__ == "__main__":
    debug_processamento()
