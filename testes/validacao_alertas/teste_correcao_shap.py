#!/usr/bin/env python3
"""
Teste focado na correção do erro SHAP
"""

import json
import numpy as np
from alertas import extrair_explicabilidade_shap

def teste_erro_shap():
    """Teste específico para validar a correção do erro SHAP."""
    
    print("🧪 Testando correção do erro SHAP...")
    
    # Simular dados SHAP como retornados pelo TreeExplainer
    feature_names = ["dist_km", "delta_t_segundos", "velocidade_kmh", "num_infracoes", 
                    "marca_modelo_igual", "tipo_igual", "cor_igual"]
    
    # Diferentes tipos de valores SHAP que podem ser retornados
    test_cases = [
        {
            "nome": "Array numpy 2D (classe binária)",
            "shap_values": np.array([0.1, 0.2, -0.1, 0.05, 0.3, -0.05, 0.08]),
            "feature_values": np.array([45.2, 3600, 85.5, 2, 1.0, 1.0, 0.0])
        },
        {
            "nome": "Array numpy 1D",
            "shap_values": np.array([0.15, -0.1, 0.25, 0.02, 0.18, -0.08, 0.12]),
            "feature_values": np.array([32.1, 1800, 120.3, 1, 0.0, 1.0, 1.0])
        },
        {
            "nome": "Lista Python",
            "shap_values": [0.08, 0.12, -0.05, 0.03, 0.22, 0.01, -0.02],
            "feature_values": [28.5, 2400, 95.8, 0, 1.0, 0.0, 1.0]
        }
    ]
    
    for i, caso in enumerate(test_cases, 1):
        print(f"\n📋 Caso {i}: {caso['nome']}")
        
        try:
            explicabilidade = extrair_explicabilidade_shap(
                shap_values=caso['shap_values'],
                feature_names=feature_names,
                feature_values=caso['feature_values'],
                modelo_id=f"TEST-RF-v1.0-Caso{i}"
            )
            
            print("✅ Explicabilidade gerada com sucesso!")
            print(f"   - Modelo: {explicabilidade['idModelo']}")
            print(f"   - Método: {explicabilidade['metodo']}")
            print(f"   - Features analisadas: {len(explicabilidade['contribuicoes'])}")
            print(f"   - Fatores de risco: {len(explicabilidade['fatoresDeRisco'])}")
            
            # Mostrar algumas contribuições
            for j, contrib in enumerate(explicabilidade['contribuicoes'][:3]):
                print(f"     {j+1}. {contrib['feature']}: valor={contrib['valor']:.3f}, impacto={contrib['impacto']:.3f}")
                
        except Exception as e:
            print(f"❌ Erro no caso {i}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n✅ Todos os casos testados com sucesso!")
    print(f"🎯 Correção do erro SHAP funcionando corretamente")
    
    return True

if __name__ == "__main__":
    if teste_erro_shap():
        print("\n🎉 Teste de correção SHAP passou!")
    else:
        print("\n❌ Teste de correção SHAP falhou!")
