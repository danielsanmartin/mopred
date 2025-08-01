"""
Teste do ARFClassifier (Adaptive Random Forest) do River
========================================================
"""

from river import forest
import numpy as np
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score

def teste_arf_oficial():
    """Teste do ARFClassifier oficial."""
    print("🌲 TESTE DO ARF CLASSIFIER OFICIAL")
    print("=" * 60)
    
    # Criar modelo conforme documentação atual
    arf = forest.ARFClassifier(
        n_models=10,           # Número de árvores
        seed=42,              # Seed para reprodutibilidade
        leaf_prediction="nba", # Naive Bayes Adaptive nas folhas
        nominal_attributes=None # Todas as features são numéricas
    )
    
    print("✅ ARFClassifier criado com sucesso")
    print(f"   📊 Parâmetros:")
    print(f"      - n_models: {arf.n_models}")
    print(f"      - seed: {arf.seed}")
    print(f"      - leaf_prediction: {arf.leaf_prediction}")
    
    # Gerar dados sintéticos similares ao problema ALPR
    X, y = make_classification(
        n_samples=1000,
        n_features=3,  # dist_km, delta_t_segundos, velocidade_kmh
        n_redundant=0,
        n_informative=3,
        n_clusters_per_class=1,
        class_sep=0.8,  # Separação entre classes
        random_state=42
    )
    
    print(f"✅ Dados sintéticos gerados:")
    print(f"   📊 {X.shape[0]} amostras, {X.shape[1]} features")
    print(f"   📊 Classes: {np.unique(y, return_counts=True)}")
    
    # Simular aprendizado online
    print("\n🔄 Iniciando aprendizado online...")
    predictions = []
    actuals = []
    accuracies = []
    
    # Warm-up period (primeiras amostras só para treino)
    warm_up = 100
    
    for i in range(len(X)):
        # Converter para formato do River
        x_dict = {
            'dist_km': float(X[i][0]),
            'delta_t_segundos': float(X[i][1]), 
            'velocidade_kmh': float(X[i][2])
        }
        
        # Fazer predição após warm-up
        if i >= warm_up:
            pred = arf.predict_one(x_dict)
            if pred is not None:
                predictions.append(int(pred))
                actuals.append(int(y[i]))
                
                # Calcular accuracy incremental
                if len(predictions) > 0:
                    acc = accuracy_score(actuals, predictions)
                    accuracies.append(acc)
        
        # Treinar com a amostra atual
        arf.learn_one(x_dict, int(y[i]))
        
        # Log de progresso
        if (i + 1) % 200 == 0:
            if len(accuracies) > 0:
                print(f"   📈 Amostra {i+1:,}: Accuracy atual = {accuracies[-1]:.3f}")
            else:
                print(f"   📈 Amostra {i+1:,}: Ainda em warm-up")
    
    # Resultados finais
    print(f"\n📊 RESULTADOS FINAIS:")
    if len(predictions) > 0:
        accuracy_final = accuracy_score(actuals, predictions)
        print(f"   🎯 Accuracy final: {accuracy_final:.3f}")
        print(f"   📊 Total de predições: {len(predictions):,}")
        print(f"   📈 Evolução da accuracy:")
        
        # Mostrar evolução em intervalos
        step = max(1, len(accuracies) // 5)
        for i in range(0, len(accuracies), step):
            print(f"      Predição {i+warm_up+1}: {accuracies[i]:.3f}")
        
        if len(accuracies) > 0:
            print(f"      Predição {len(accuracies)+warm_up}: {accuracies[-1]:.3f}")
    else:
        print("   ❌ Nenhuma predição foi feita")
    
    print(f"\n🎉 Teste concluído com sucesso!")
    return arf

def teste_comparacao_batch_vs_online():
    """Compara o desempenho do ARF com dados em lote vs online."""
    print(f"\n🔄 COMPARAÇÃO: BATCH vs ONLINE LEARNING")
    print("=" * 60)
    
    # Gerar dois conjuntos de dados para simular mudança temporal
    print("📦 Gerando dados com mudança temporal...")
    
    # Período 1: Comportamento normal
    X1, y1 = make_classification(
        n_samples=300,
        n_features=3,
        n_redundant=0,
        n_informative=3,
        n_clusters_per_class=1,
        class_sep=0.8,
        random_state=42
    )
    
    # Período 2: Mudança no padrão (mais ruído)
    X2, y2 = make_classification(
        n_samples=300,
        n_features=3,
        n_redundant=0,
        n_informative=3,
        n_clusters_per_class=1,
        class_sep=0.4,  # Menor separação = mais difícil
        random_state=123
    )
    
    # Combinar dados
    X_total = np.vstack([X1, X2])
    y_total = np.hstack([y1, y2])
    
    print(f"   ✅ Período 1: {len(X1)} amostras (fácil)")
    print(f"   ✅ Período 2: {len(X2)} amostras (difícil)")
    
    # Criar dois modelos
    arf_online = forest.ARFClassifier(
        n_models=10, seed=42, leaf_prediction="nba"
    )
    
    arf_retrain = forest.ARFClassifier(
        n_models=10, seed=42, leaf_prediction="nba"
    )
    
    print("\n🔄 Testando aprendizado online contínuo...")
    
    # Modelo online: aprende continuamente
    predictions_online = []
    actuals_online = []
    
    for i in range(len(X_total)):
        x_dict = {f'feature_{j}': float(X_total[i][j]) for j in range(3)}
        
        if i >= 50:  # Após warm-up
            pred = arf_online.predict_one(x_dict)
            if pred is not None:
                predictions_online.append(int(pred))
                actuals_online.append(int(y_total[i]))
        
        arf_online.learn_one(x_dict, int(y_total[i]))
    
    # Modelo com retreinamento: treina só no período 1, testa no período 2
    print("🔄 Testando modelo com retreinamento...")
    
    # Treinar apenas no período 1
    for i in range(len(X1)):
        x_dict = {f'feature_{j}': float(X1[i][j]) for j in range(3)}
        arf_retrain.learn_one(x_dict, int(y1[i]))
    
    # Testar apenas no período 2
    predictions_retrain = []
    actuals_retrain = []
    
    for i in range(len(X2)):
        x_dict = {f'feature_{j}': float(X2[i][j]) for j in range(3)}
        pred = arf_retrain.predict_one(x_dict)
        if pred is not None:
            predictions_retrain.append(int(pred))
            actuals_retrain.append(int(y2[i]))
    
    # Comparar resultados
    print(f"\n📊 COMPARAÇÃO DE RESULTADOS:")
    
    if len(predictions_online) > 0:
        acc_online = accuracy_score(actuals_online, predictions_online)
        print(f"   🔄 Aprendizado Online: {acc_online:.3f}")
    
    if len(predictions_retrain) > 0:
        acc_retrain = accuracy_score(actuals_retrain, predictions_retrain)
        print(f"   📦 Modelo Estático: {acc_retrain:.3f}")
        
        if len(predictions_online) > 0:
            diff = acc_online - acc_retrain
            if diff > 0:
                print(f"   🏆 Vantagem do Online: +{diff:.3f}")
            else:
                print(f"   📉 Desvantagem do Online: {diff:.3f}")
    
    return arf_online, arf_retrain

if __name__ == "__main__":
    try:
        # Teste básico
        arf = teste_arf_oficial()
        
        # Teste de comparação
        arf_online, arf_static = teste_comparacao_batch_vs_online()
        
        print(f"\n🏆 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
