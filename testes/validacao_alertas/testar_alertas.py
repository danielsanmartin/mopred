"""
Teste do Módulo de Alertas JSON-LD
==================================

Script de teste para validar a geração de alertas conforme especificação da tese.
"""

import sys
import os

# Adicionar a raiz do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from alertas import GeradorAlertasSimples, extrair_explicabilidade_shap
import json

def testar_gerador_alertas():
    """Testa a geração de alertas com dados simulados."""
    
    print("🧪 TESTANDO GERADOR DE ALERTAS JSON-LD")
    print("=" * 50)
    
    # Criar gerador de alertas
    gerador = GeradorAlertasSimples(
        identificador_sistema="MOPRED-SC-01-TESTE",
        limiar_alerta=0.80
    )
    
    # Dados simulados de uma passagem suspeita
    passagem_exemplo = {
        "placa": "QRT5E67",
        "escore": 0.92,
        "timestampDeteccao": "2025-10-26T14:29:50Z",
        "lat": -27.59537,
        "lon": -48.54805,
        "descricaoArea": "Proximidades da Ponte Hercílio Luz, Florianópolis, SC",
        "modeloInferido": "Fiat Cronos (Branco)"
    }
    
    # Dados simulados de explicabilidade SHAP
    explicabilidade_exemplo = {
        "idModelo": "RF-v2.1.3",
        "metodo": "SHAP",
        "contribuicoes": [
            {"feature": "Velocidade estimada (km/h)", "valor": 145.2, "impacto": 0.31, "sinal": "+"},
            {"feature": "Distância entre câmeras (km)", "valor": 85.7, "impacto": 0.22, "sinal": "+"},
            {"feature": "Número de infrações", "valor": 12.0, "impacto": 0.18, "sinal": "+"}
        ],
        "fatoresDeRisco": [
            "Rota incomum para o dia/horário.",
            "Velocidade incompatível com o fluxo da via."
        ]
    }
    
    # Recursos adicionais
    recursos_exemplo = [
        {
            "descricaoRecurso": "Evidência Visual",
            "mimeType": "video/mp4",
            "uri": "/api/v1/recursos/video/a1b2c3d4"
        }
    ]
    
    # Gerar alerta
    print("1. Gerando alerta individual...")
    alerta = gerador.criar_alerta(
        passagem_exemplo, 
        explicabilidade_exemplo, 
        recursos_exemplo
    )
    
    print("✅ Alerta gerado com sucesso!")
    print(f"ID: {alerta['id']}")
    print(f"Severidade: {alerta['info']['severidade']}")
    print(f"Score: {passagem_exemplo['escore']}")
    
    # Exibir JSON completo
    print("\n2. Alerta em formato JSON-LD:")
    print(gerador.to_json(alerta, indent=2))
    
    # Teste de processamento em lote
    print("\n3. Testando processamento em lote...")
    
    pares_exemplo = [
        {"placa": "ABC1234", "lat": -27.5954, "lon": -48.5480, "descricaoArea": "Centro de Florianópolis", "modeloInferido": "Civic (Prata)"},
        {"placa": "XYZ9876", "lat": -26.3045, "lon": -48.8487, "descricaoArea": "Centro de Joinville", "modeloInferido": "Corolla (Branco)"},
        {"placa": "DEF5678", "lat": -27.1000, "lon": -52.6152, "descricaoArea": "Centro de Chapecó", "modeloInferido": "HB20 (Azul)"}
    ]
    
    scores_exemplo = [0.85, 0.75, 0.95]  # Apenas o primeiro e terceiro devem gerar alertas
    
    alertas_lote = gerador.processar_batch_alertas(pares_exemplo, scores_exemplo)
    
    print(f"✅ {len(alertas_lote)} alertas gerados em lote (esperado: 2)")
    
    for i, alerta in enumerate(alertas_lote):
        print(f"   Alerta {i+1}: {alerta['info']['parametrosPreditivos'][0]['valor']} - Score: {alerta['info']['parametrosPreditivos'][1]['valor']}")
    
    # Salvar alertas de teste
    print("\n4. Salvando alertas de teste...")
    with open("alertas_teste.ndjson", "w", encoding="utf-8") as f:
        f.write(gerador.to_json(alerta, indent=0) + "\n")
        for alerta_lote in alertas_lote:
            f.write(gerador.to_json(alerta_lote, indent=0) + "\n")
    
    print("✅ Alertas salvos em: alertas_teste.ndjson")
    
    # Teste de validação de limiar
    print("\n5. Testando validação de limiar...")
    print(f"Score 0.95 deve gerar alerta: {gerador.deve_gerar_alerta(0.95)}")
    print(f"Score 0.75 deve gerar alerta: {gerador.deve_gerar_alerta(0.75)}")
    print(f"Score 0.60 deve gerar alerta: {gerador.deve_gerar_alerta(0.60)}")
    
    print("\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")

if __name__ == "__main__":
    testar_gerador_alertas()
