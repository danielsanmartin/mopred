"""
Script para verificar se veículos clonados estão sendo gerados com características diferentes.
"""

import pandas as pd
import numpy as np
from simulador_streaming_alpr import SimuladorStreamingALPR
from utils import processar_placa_basico

def verificar_caracteristicas_clones():
    """Verifica se veículos clonados têm características diferentes."""
    print("🔍 VERIFICANDO CARACTERÍSTICAS DOS VEÍCULOS CLONADOS")
    print("=" * 60)
    
    # Inicializar simulador
    simulador = SimuladorStreamingALPR("configs/config.json")
    
    # Gerar alguns eventos para teste
    eventos = simulador.executar_simulacao_completa()
    
    if not eventos:
        print("❌ Nenhum evento gerado")
        return
    
    print(f"✅ {len(eventos):,} eventos gerados")
    
    # Converter eventos para DataFrame
    eventos_dict = [evento.to_dict() for evento in eventos]
    df_eventos = pd.DataFrame(eventos_dict)
    
    # Filtrar apenas veículos clonados
    clonados = df_eventos[df_eventos['is_clonado'] == True]
    
    if len(clonados) == 0:
        print("❌ Nenhum veículo clonado encontrado")
        return
    
    print(f"📊 {len(clonados):,} eventos de veículos clonados encontrados")
    
    # Analisar características por placa
    placas_clonadas = clonados['placa'].unique()
    print(f"🏷️ {len(placas_clonadas)} placas clonadas únicas")
    
    # Verificar variações de características para cada placa clonada
    print("\n🔎 ANÁLISE DE VARIAÇÕES POR PLACA CLONADA:")
    print("-" * 60)
    
    total_pares = 0
    pares_marca_modelo_diferentes = 0
    pares_tipo_diferentes = 0
    pares_cor_diferentes = 0
    
    for placa in placas_clonadas[:10]:  # Verificar primeiras 10 placas
        eventos_placa = clonados[clonados['placa'] == placa].sort_values('timestamp')
        
        if len(eventos_placa) < 2:
            continue
            
        print(f"\n📍 Placa: {placa} ({len(eventos_placa)} eventos)")
        
        # Verificar se há variações nas características
        marcas_unicas = eventos_placa['marca'].nunique()
        modelos_unicos = eventos_placa['modelo'].nunique()
        tipos_unicos = eventos_placa['tipo'].nunique()
        cores_unicas = eventos_placa['cor'].nunique()
        
        print(f"   Marcas únicas: {marcas_unicas}")
        print(f"   Modelos únicos: {modelos_unicos}")
        print(f"   Tipos únicos: {tipos_unicos}")
        print(f"   Cores únicas: {cores_unicas}")
        
        if marcas_unicas > 1 or modelos_unicos > 1:
            print("   ⚠️ MARCA/MODELO VARIANDO!")
        if tipos_unicos > 1:
            print("   ⚠️ TIPO VARIANDO!")
        if cores_unicas > 1:
            print("   ⚠️ COR VARIANDO!")
        
        # Analisar pares consecutivos
        for i in range(len(eventos_placa) - 1):
            evento1 = eventos_placa.iloc[i]
            evento2 = eventos_placa.iloc[i + 1]
            
            total_pares += 1
            
            # Verificar se marca/modelo são diferentes
            if evento1['marca'] != evento2['marca'] or evento1['modelo'] != evento2['modelo']:
                pares_marca_modelo_diferentes += 1
                print(f"     Par {i+1}-{i+2}: MARCA/MODELO diferentes - "
                      f"{evento1['marca']}/{evento1['modelo']} vs {evento2['marca']}/{evento2['modelo']}")
            
            # Verificar se tipo é diferente
            if evento1['tipo'] != evento2['tipo']:
                pares_tipo_diferentes += 1
                print(f"     Par {i+1}-{i+2}: TIPO diferente - {evento1['tipo']} vs {evento2['tipo']}")
            
            # Verificar se cor é diferente
            if evento1['cor'] != evento2['cor']:
                pares_cor_diferentes += 1
                print(f"     Par {i+1}-{i+2}: COR diferente - {evento1['cor']} vs {evento2['cor']}")
    
    # Estatísticas finais
    print(f"\n📈 ESTATÍSTICAS FINAIS:")
    print(f"Total de pares analisados: {total_pares}")
    print(f"Pares com marca/modelo diferentes: {pares_marca_modelo_diferentes} ({pares_marca_modelo_diferentes/total_pares*100:.1f}%)")
    print(f"Pares com tipo diferente: {pares_tipo_diferentes} ({pares_tipo_diferentes/total_pares*100:.1f}%)")
    print(f"Pares com cor diferente: {pares_cor_diferentes} ({pares_cor_diferentes/total_pares*100:.1f}%)")
    
    # Testar a função de processamento básico
    print(f"\n🧪 TESTANDO FUNÇÃO DE PROCESSAMENTO BÁSICO:")
    print("-" * 60)
    
    # Processar algumas placas para ver os valores das features
    placas_teste = placas_clonadas[:3]
    for placa in placas_teste:
        eventos_placa = df_eventos[df_eventos['placa'] == placa].sort_values('timestamp')
        
        if len(eventos_placa) < 2:
            continue
            
        print(f"\n🔬 Processando placa: {placa}")
        
        try:
            features, labels, features_semelhanca = processar_placa_basico(eventos_placa)
            
            if len(features_semelhanca) > 0:
                # Pegar primeira feature completa
                primeira_feature = features_semelhanca[0]
                print(f"   Features: {primeira_feature}")
                print(f"   dist_km: {primeira_feature[0]:.3f}")
                print(f"   delta_t_segundos: {primeira_feature[1]:.3f}")
                print(f"   velocidade_kmh: {primeira_feature[2]:.3f}")
                print(f"   num_infracoes: {primeira_feature[3]:.3f}")
                print(f"   marca_modelo_igual: {primeira_feature[4]:.1f}")
                print(f"   tipo_igual: {primeira_feature[5]:.1f}")
                print(f"   cor_igual: {primeira_feature[6]:.1f}")
                
                # Verificar se alguma característica é diferente (valor 0.0)
                if primeira_feature[4] == 0.0:
                    print("   ⚠️ MARCA/MODELO DIFERENTES DETECTADOS!")
                if primeira_feature[5] == 0.0:
                    print("   ⚠️ TIPO DIFERENTE DETECTADO!")
                if primeira_feature[6] == 0.0:
                    print("   ⚠️ COR DIFERENTE DETECTADA!")
            else:
                print("   ❌ Nenhuma feature gerada")
                
        except Exception as e:
            print(f"   ❌ Erro ao processar: {e}")

if __name__ == "__main__":
    verificar_caracteristicas_clones()
