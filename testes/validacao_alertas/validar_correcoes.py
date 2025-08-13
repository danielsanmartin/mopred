#!/usr/bin/env python3
"""
Teste rápido das correções implementadas
"""

import json
import sys
import os

def teste_rapido_correcoes():
    """Teste rápido das principais correções."""
    
    print("🧪 Teste rápido das correções implementadas...")
    
    # 1. Testar correção SHAP
    print("\n1️⃣ Testando correção SHAP...")
    try:
        from alertas import extrair_explicabilidade_shap
        import numpy as np
        
        shap_values = np.array([0.1, 0.2, -0.1])
        feature_names = ["dist_km", "velocidade_kmh", "num_infracoes"]
        feature_values = np.array([45.2, 85.5, 2])
        
        resultado = extrair_explicabilidade_shap(
            shap_values, feature_names, feature_values, "TEST-RF"
        )
        
        print("✅ Correção SHAP funcionando!")
        print(f"   Método: {resultado['metodo']}")
        print(f"   Contribuições: {len(resultado['contribuicoes'])}")
        
    except Exception as e:
        print(f"❌ Erro na correção SHAP: {e}")
        return False
    
    # 2. Testar formatação JSON
    print("\n2️⃣ Testando formatação JSON...")
    try:
        from alertas import GeradorAlertasSimples
        
        alerta_teste = {
            "@context": "https://www.mopred.org/schemas/alerta/v1",
            "@type": "AlertaPreditivo",
            "id": "test-123",
            "info": {"teste": "dados"}
        }
        
        json_compacto = GeradorAlertasSimples.to_json(alerta_teste, indent=None)
        json_formatado = GeradorAlertasSimples.to_json(alerta_teste, indent=2)
        
        quebras_compacto = json_compacto.count('\n')
        quebras_formatado = json_formatado.count('\n')
        
        print("✅ Formatação JSON funcionando!")
        print(f"   JSON compacto: {quebras_compacto} quebras de linha")
        print(f"   JSON formatado: {quebras_formatado} quebras de linha")
        
        if quebras_compacto == 0:
            print("✅ NDJSON correto (sem quebras de linha)")
        else:
            print("❌ NDJSON incorreto (tem quebras de linha)")
            return False
            
    except Exception as e:
        print(f"❌ Erro na formatação JSON: {e}")
        return False
    
    # 3. Verificar se configuração está carregando
    print("\n3️⃣ Testando carregamento de configuração...")
    try:
        with open('configs/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Configuração carregada!")
        print(f"   Gerar alertas: {config.get('gerar_alertas', 'não definido')}")
        print(f"   Limiar alertas: {config.get('limiar_alertas', 'não definido')}")
        
    except Exception as e:
        print(f"⚠️ Erro ao carregar config: {e}")
    
    print("\n🎉 Todas as correções principais estão funcionando!")
    return True

if __name__ == "__main__":
    if teste_rapido_correcoes():
        print("\n✅ Pronto para executar teste completo!")
        print("💡 Execute: python validacao_modelo_conceitual.py")
    else:
        print("\n❌ Ainda há problemas nas correções")
        sys.exit(1)
