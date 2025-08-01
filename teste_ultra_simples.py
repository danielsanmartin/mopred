import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

print("🧪 TESTE BÁSICO DE MODELOS")
print("=" * 40)

# Carregar dados
df = pd.read_csv("passagens_streaming.csv")
print(f"✅ Dados: {len(df):,} registros")

# Placas com 2+ passagens
placas_counts = df['placa'].value_counts()
placas_multiplas = placas_counts[placas_counts >= 2].head(1000)
print(f"📊 Placas múltiplas: {len(placas_multiplas)}")

# Gerar features básicas
features = []
labels = []

for placa in placas_multiplas.index[:500]:
    eventos = df[df['placa'] == placa].head(2)
    if len(eventos) < 2:
        continue
    
    e1, e2 = eventos.iloc[0], eventos.iloc[1]
    
    # Feature simples: diferença de tempo
    delta_t = abs(e2['timestamp'] - e1['timestamp']) / 1000 / 3600  # horas
    
    features.append([delta_t])
    labels.append(1 if delta_t < 0.1 else 0)  # Suspeito se < 6min

X = np.array(features)
y = np.array(labels)

print(f"📊 Features: {len(X)}, Suspeitos: {sum(y)}")

if len(X) < 10:
    print("❌ Poucos dados")
    exit()

# Dividir dados
split1 = len(X) // 3
split2 = 2 * len(X) // 3

X_treino = X[:split1]
y_treino = y[:split1]
X_teste1 = X[split1:split2]
y_teste1 = y[split1:split2]
X_teste2 = X[split2:]
y_teste2 = y[split2:]

print(f"📊 Treino: {len(X_treino)}, Teste1: {len(X_teste1)}, Teste2: {len(X_teste2)}")

# Modelos
modelo_trad = RandomForestClassifier(n_estimators=10, random_state=42)
modelo_adapt = RandomForestClassifier(n_estimators=10, random_state=42)

# Treinar
modelo_trad.fit(X_treino, y_treino)
modelo_adapt.fit(X_treino, y_treino)

print("\n🧪 TESTE JANELA 1:")
pred_trad_1 = modelo_trad.predict(X_teste1)
pred_adapt_1 = modelo_adapt.predict(X_teste1)

acc_trad_1 = accuracy_score(y_teste1, pred_trad_1)
acc_adapt_1 = accuracy_score(y_teste1, pred_adapt_1)

print(f"Tradicional: {acc_trad_1:.3f}")
print(f"Adaptativo:  {acc_adapt_1:.3f}")

# Retreinar adaptativo
print("\n🔄 Retreinando modelo adaptativo...")
X_novo = np.vstack([X_treino, X_teste1])
y_novo = np.hstack([y_treino, y_teste1])
modelo_adapt.fit(X_novo, y_novo)

print("\n🧪 TESTE JANELA 2:")
pred_trad_2 = modelo_trad.predict(X_teste2)
pred_adapt_2 = modelo_adapt.predict(X_teste2)

acc_trad_2 = accuracy_score(y_teste2, pred_trad_2)
acc_adapt_2 = accuracy_score(y_teste2, pred_adapt_2)

print(f"Tradicional: {acc_trad_2:.3f}")
print(f"Adaptativo:  {acc_adapt_2:.3f}")

print("\n📈 RESULTADO:")
if acc_adapt_2 > acc_trad_2:
    print("🏆 Vencedor: Adaptativo")
elif acc_trad_2 > acc_adapt_2:
    print("🏆 Vencedor: Tradicional")
else:
    print("🤝 Empate")

print("✅ Teste concluído!")
