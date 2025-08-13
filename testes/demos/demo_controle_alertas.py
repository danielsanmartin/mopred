"""
Teste de Controle de Alertas via Configuração
=============================================

Demonstra como ativar/desativar a geração de alertas através do config.json
"""

import json

def demonstrar_controle_alertas():
    """Demonstra diferentes configurações de alertas."""
    
    print("🧪 DEMONSTRAÇÃO DO CONTROLE DE ALERTAS VIA CONFIG.JSON")
    print("=" * 60)
    
    # Configuração atual
    with open('configs/config.json', 'r', encoding='utf-8') as f:
        config_atual = json.load(f)
    
    print("📋 Configuração atual de alertas:")
    print(f"   gerar_alertas: {config_atual.get('gerar_alertas', 'não definido')}")
    print(f"   limiar_alertas: {config_atual.get('limiar_alertas', 'não definido')}")
    print(f"   identificador_sistema_alertas: {config_atual.get('identificador_sistema_alertas', 'não definido')}")
    
    # Exemplo 1: Alertas habilitados (padrão)
    config_exemplo_1 = {
        "gerar_alertas": True,
        "limiar_alertas": 0.80,
        "identificador_sistema_alertas": "MOPRED-SC-01"
    }
    
    print(f"\n📤 EXEMPLO 1 - Alertas Habilitados:")
    print(f"   ✅ Alertas serão gerados para scores >= 0.80")
    print(f"   📁 Arquivos: alertas_janela_XXX.ndjson, alertas_consolidados.ndjson")
    print(f"   🏷️ Sistema: MOPRED-SC-01")
    
    # Exemplo 2: Alertas desabilitados
    config_exemplo_2 = {
        "gerar_alertas": False,
        "limiar_alertas": 0.80,
        "identificador_sistema_alertas": "MOPRED-SC-01"
    }
    
    print(f"\n🚫 EXEMPLO 2 - Alertas Desabilitados:")
    print(f"   ❌ Nenhum alerta será gerado")
    print(f"   📊 Apenas métricas e relatórios SHAP")
    print(f"   💾 Reduz overhead de processamento")
    
    # Exemplo 3: Limiar personalizado
    config_exemplo_3 = {
        "gerar_alertas": True,
        "limiar_alertas": 0.95,
        "identificador_sistema_alertas": "MOPRED-TESTE-ALTA-PRECISAO"
    }
    
    print(f"\n🎯 EXEMPLO 3 - Limiar Alto (Precisão):")
    print(f"   ⚡ Alertas apenas para scores >= 0.95")
    print(f"   🔍 Foco em casos de altíssima suspeição")
    print(f"   🏷️ Sistema: MOPRED-TESTE-ALTA-PRECISAO")
    
    # Exemplo 4: Limiar baixo (Recall)
    config_exemplo_4 = {
        "gerar_alertas": True,
        "limiar_alertas": 0.60,
        "identificador_sistema_alertas": "MOPRED-TESTE-ALTA-SENSIBILIDADE"
    }
    
    print(f"\n📡 EXEMPLO 4 - Limiar Baixo (Sensibilidade):")
    print(f"   📈 Alertas para scores >= 0.60")
    print(f"   🔎 Captura mais casos suspeitos")
    print(f"   ⚠️ Pode gerar mais falsos positivos")
    
    print(f"\n🔧 COMO USAR:")
    print(f"   1. Edite o arquivo config.json")
    print(f"   2. Modifique as propriedades:")
    print(f"      - gerar_alertas: true/false")
    print(f"      - limiar_alertas: 0.0-1.0")
    print(f"      - identificador_sistema_alertas: \"NOME_SISTEMA\"")
    print(f"   3. Execute: python validacao_modelo_conceitual.py")
    
    print(f"\n📊 BENEFÍCIOS DO CONTROLE:")
    print(f"   🎛️ Flexibilidade: Liga/desliga conforme necessidade")
    print(f"   ⚡ Performance: Desabilita em testes de desenvolvimento")
    print(f"   🎯 Precisão: Ajusta limiar conforme estratégia")
    print(f"   🏷️ Organização: Identifica diferentes experimentos")
    
    # Salvar exemplos de configuração
    exemplos = {
        "exemplo_1_habilitado": config_exemplo_1,
        "exemplo_2_desabilitado": config_exemplo_2,
        "exemplo_3_alta_precisao": config_exemplo_3,
        "exemplo_4_alta_sensibilidade": config_exemplo_4
    }
    
    with open("exemplos_config_alertas.json", "w", encoding="utf-8") as f:
        json.dump(exemplos, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Exemplos salvos em: exemplos_config_alertas.json")
    print(f"✅ Demonstração concluída!")

if __name__ == "__main__":
    demonstrar_controle_alertas()
