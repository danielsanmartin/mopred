"""
Teste básico do River Adaptive Random Forest
============================================
"""

from river import ensemble, tree
import numpy as np
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score

def teste_river_basico():
    """Teste básico para verificar se o River está funcionando."""
    print("🧪 TESTE BÁSICO DO RIVER ADAPTIVE RANDOM FOREST")
    print("=" * 50)
    
    # Criar modelo AdaptiveRandomForestClassifier
    arf = ensemble.AdaptiveRandomForestClassifier(
        n_models=10,
        seed=42,
        leaf_prediction="nba",  # Naive Bayes Adaptive
        nominal_attributes=None
    )
    
    print("✅ Modelo criado com sucesso")
    
    # Gerar dados sintéticos
    X, y = make_classification(
        n_samples=1000,
        n_features=3,
        n_redundant=0,
        n_informative=3,
        n_clusters_per_class=1,
        random_state=42
    )
    
    print(f"✅ Dados gerados: {X.shape[0]} amostras, {X.shape[1]} features")
    
    # Treinar incrementalmente
    print("🔄 Treinando modelo incrementalmente...")
    predictions = []
    actuals = []
    
    for i in range(len(X)):
        # Converter para formato do River (dicionário)
        x_dict = {f'feature_{j}': float(X[i][j]) for j in range(X.shape[1])}
        
        # Fazer predição antes do treinamento (online learning)
        if i > 50:  # Começar a avaliar após algumas amostras
            pred = arf.predict_one(x_dict)
            if pred is not None:
                predictions.append(int(pred))
                actuals.append(int(y[i]))
        
        # Treinar com a amostra atual
        arf.learn_one(x_dict, int(y[i]))
        
        if (i + 1) % 100 == 0:
            print(f"   Processadas {i + 1:,} amostras")
    
    # Calcular accuracy
    if len(predictions) > 0:
        accuracy = accuracy_score(actuals, predictions)
        print(f"✅ Accuracy final: {accuracy:.3f}")
        print(f"📊 Total de predições avaliadas: {len(predictions):,}")
    else:
        print("⚠️ Nenhuma predição foi feita")
    
    print("\n🎉 Teste concluído com sucesso!")
    return arf

def teste_wrapper():
    """Teste do wrapper personalizado."""
    print("\n🧪 TESTE DO WRAPPER PERSONALIZADO")
    print("=" * 50)
    
    from comparador_modelos import AdaptiveRandomForestWrapper
    
    # Criar wrapper
    wrapper = AdaptiveRandomForestWrapper(n_models=5, seed=42)
    print("✅ Wrapper criado com sucesso")
    
    # Gerar dados para teste
    X, y = make_classification(
        n_samples=200,
        n_features=3,
        n_redundant=0,
        n_informative=3,
        random_state=42
    )
    
    # Dividir em treino e teste
    X_treino = X[:150]
    y_treino = y[:150]
    X_teste = X[150:]
    y_teste = y[150:]
    
    print(f"✅ Dados preparados: {len(X_treino)} treino, {len(X_teste)} teste")
    
    # Treinar
    print("🔄 Treinando wrapper...")
    wrapper.learn_batch(X_treino, y_treino)
    
    # Predizer
    print("🔮 Fazendo predições...")
    y_pred = wrapper.predict_batch(X_teste)
    
    # Avaliar
    accuracy = accuracy_score(y_teste, y_pred)
    print(f"✅ Accuracy do wrapper: {accuracy:.3f}")
    print(f"📊 Predições: {len(y_pred)}")
    
    print("\n🎉 Teste do wrapper concluído!")
    return wrapper

if __name__ == "__main__":
    try:
        # Teste básico do River
        arf = teste_river_basico()
        
        # Teste do wrapper
        wrapper = teste_wrapper()
        
        print("\n🏆 TODOS OS TESTES PASSARAM!")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
