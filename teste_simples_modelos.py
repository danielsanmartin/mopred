"""
Teste Simplificado de Modelos Temporais
=======================================

Versão simplificada para debug e teste inicial.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def teste_simples():
    """Teste simplificado dos modelos."""
    print("🧪 INICIANDO TESTE SIMPLIFICADO")
    print("=" * 50)
    
    try:
        # 1. Carregar dados existentes
        if pd.io.common.file_exists("passagens_streaming.csv"):
            df = pd.read_csv("passagens_streaming.csv")
            print(f"✅ Dados carregados: {len(df):,} registros")
        else:
            print("❌ Arquivo passagens_streaming.csv não encontrado")
            return
        
        # 2. Gerar features simples
        print("🔧 Gerando features...")
        
        from haversine import haversine
        
        features = []
        labels = []
        
        # Pegar placas com múltiplas passagens
        placas_counts = df['placa'].value_counts()
        placas_multiplas = placas_counts[placas_counts > 1].index
        
        print(f"📊 Placas com múltiplas passagens: {len(placas_multiplas)}")
        
        for placa in placas_multiplas[:500]:  # Limitar para teste
            eventos_placa = df[df['placa'] == placa].sort_values('timestamp')
            
            if len(eventos_placa) < 2:
                continue
            
            # Gerar par consecutivo
            evento1 = eventos_placa.iloc[0]
            evento2 = eventos_placa.iloc[1]
            
            # Calcular features básicas
            dist_km = haversine(
                (evento1['lat'], evento1['lon']),
                (evento2['lat'], evento2['lon'])
            )
            
            delta_t_ms = abs(evento2['timestamp'] - evento1['timestamp'])
            delta_t_segundos = delta_t_ms / 1000
            
            if delta_t_segundos < 30:  # Muito rápido
                continue
            
            velocidade_kmh = (dist_km / (delta_t_segundos / 3600)) if delta_t_segundos > 0 else 0
            
            # Features: [distância, tempo, velocidade]
            feature_vector = [dist_km, delta_t_segundos, velocidade_kmh]
            features.append(feature_vector)
            
            # Label: suspeito se velocidade > 150 km/h
            label = 1 if velocidade_kmh > 150 else 0
            labels.append(label)
        
        features = np.array(features)
        labels = np.array(labels)
        
        print(f"✅ Features geradas: {len(features):,} pares")
        print(f"   ⚠️ Casos suspeitos: {sum(labels):,} ({sum(labels)/len(labels)*100:.1f}%)")
        
        if len(features) < 10:
            print("❌ Poucos dados para teste")
            return
        
        # 3. Dividir dados em janelas temporais
        print("🪟 Dividindo em janelas temporais...")
        
        janela1_size = len(features) // 3
        janela2_size = len(features) // 3
        
        # Janela 1: Treino inicial
        X_treino = features[:janela1_size]
        y_treino = labels[:janela1_size]
        
        # Janela 2: Primeira avaliação
        X_teste1 = features[janela1_size:janela1_size+janela2_size]
        y_teste1 = labels[janela1_size:janela1_size+janela2_size]
        
        # Janela 3: Segunda avaliação (mudança simulada)
        X_teste2 = features[janela1_size+janela2_size:]
        y_teste2 = labels[janela1_size+janela2_size:]
        
        # Simular mudança nos dados da janela 3 (mais casos suspeitos)
        # Alterar alguns labels para simular mudança de padrão
        y_teste2_modificado = y_teste2.copy()
        for i in range(0, len(y_teste2_modificado), 3):  # A cada 3 casos
            y_teste2_modificado[i] = 1  # Forçar como suspeito
        
        print(f"📊 Divisão dos dados:")
        print(f"   Treino: {len(X_treino):,} amostras")
        print(f"   Teste 1: {len(X_teste1):,} amostras")
        print(f"   Teste 2: {len(X_teste2):,} amostras (modificado)")
        
        # 4. Treinar modelo tradicional
        print("\n🌳 Treinando Random Forest Tradicional...")
        
        modelo_tradicional = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42
        )
        modelo_tradicional.fit(X_treino, y_treino)
        
        print("✅ Modelo tradicional treinado")
        
        # 5. Modelo adaptativo simples (retreina a cada janela)
        print("🔄 Preparando modelo adaptativo...")
        
        # Modelo adaptativo = modelo tradicional que retreina
        modelo_adaptativo = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42
        )
        modelo_adaptativo.fit(X_treino, y_treino)  # Treino inicial
        
        # 6. Testar em múltiplas janelas
        print("\n📊 TESTANDO EM JANELAS TEMPORAIS")
        print("=" * 50)
        
        resultados = []
        
        # Janela 1
        print("\n📊 JANELA 1 (baseline):")
        pred_trad_1 = modelo_tradicional.predict(X_teste1)
        pred_adapt_1 = modelo_adaptativo.predict(X_teste1)
        
        acc_trad_1 = accuracy_score(y_teste1, pred_trad_1)
        acc_adapt_1 = accuracy_score(y_teste1, pred_adapt_1)
        f1_trad_1 = f1_score(y_teste1, pred_trad_1, zero_division=0)
        f1_adapt_1 = f1_score(y_teste1, pred_adapt_1, zero_division=0)
        
        print(f"Tradicional - Accuracy: {acc_trad_1:.3f}, F1: {f1_trad_1:.3f}")
        print(f"Adaptativo  - Accuracy: {acc_adapt_1:.3f}, F1: {f1_adapt_1:.3f}")
        
        resultados.append({
            'janela': 1,
            'tradicional_acc': acc_trad_1,
            'tradicional_f1': f1_trad_1,
            'adaptativo_acc': acc_adapt_1,
            'adaptativo_f1': f1_adapt_1
        })
        
        # Janela 2 (modelo adaptativo retreina)
        print("\n📊 JANELA 2 (após retreino adaptativo):")
        
        # Retreinar modelo adaptativo com dados das janelas anteriores
        X_retreino = np.vstack([X_treino, X_teste1])
        y_retreino = np.hstack([y_treino, y_teste1])
        modelo_adaptativo.fit(X_retreino, y_retreino)
        
        pred_trad_2 = modelo_tradicional.predict(X_teste2)  # Modelo original
        pred_adapt_2 = modelo_adaptativo.predict(X_teste2)  # Modelo retreinado
        
        acc_trad_2 = accuracy_score(y_teste2_modificado, pred_trad_2)
        acc_adapt_2 = accuracy_score(y_teste2_modificado, pred_adapt_2)
        f1_trad_2 = f1_score(y_teste2_modificado, pred_trad_2, zero_division=0)
        f1_adapt_2 = f1_score(y_teste2_modificado, pred_adapt_2, zero_division=0)
        
        print(f"Tradicional - Accuracy: {acc_trad_2:.3f}, F1: {f1_trad_2:.3f}")
        print(f"Adaptativo  - Accuracy: {acc_adapt_2:.3f}, F1: {f1_adapt_2:.3f}")
        
        resultados.append({
            'janela': 2,
            'tradicional_acc': acc_trad_2,
            'tradicional_f1': f1_trad_2,
            'adaptativo_acc': acc_adapt_2,
            'adaptativo_f1': f1_adapt_2
        })
        
        # 7. Relatório final
        print("\n📈 RELATÓRIO FINAL")
        print("=" * 50)
        
        for resultado in resultados:
            janela = resultado['janela']
            print(f"\nJanela {janela}:")
            print(f"  Tradicional: Acc={resultado['tradicional_acc']:.3f}, F1={resultado['tradicional_f1']:.3f}")
            print(f"  Adaptativo:  Acc={resultado['adaptativo_acc']:.3f}, F1={resultado['adaptativo_f1']:.3f}")
            
            if resultado['adaptativo_f1'] > resultado['tradicional_f1']:
                print(f"  🏆 Vencedor: Adaptativo")
            elif resultado['tradicional_f1'] > resultado['adaptativo_f1']:
                print(f"  🏆 Vencedor: Tradicional")
            else:
                print(f"  🤝 Empate")
        
        # Salvar resultados
        df_resultados = pd.DataFrame(resultados)
        df_resultados.to_csv('teste_simples_resultados.csv', index=False)
        print(f"\n💾 Resultados salvos em: teste_simples_resultados.csv")
        
        return resultados
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_simples()
