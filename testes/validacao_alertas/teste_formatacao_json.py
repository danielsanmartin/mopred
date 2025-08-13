#!/usr/bin/env python3
"""
Teste direto da formatação JSON dos alertas.
"""

import json
from alertas import GeradorAlertasSimples

def teste_formatacao_json():
    """Testa diretamente a formatação JSON dos alertas."""
    
    print("🧪 Testando formatação JSON direta...")
    
    # Cria gerador de alertas
    gerador = GeradorAlertasSimples(
        identificador_sistema="TESTE-FORMATACAO",
        limiar_alerta=0.8
    )
    
    # Dados simulados para um alerta
    par_info = {
        'placa': 'ABC1234',
        'lat': -27.5969,
        'lon': -48.5495,
        'timestamp': 1640995200000,
        'cam': 'CAM_01',
        'é_clone': True,
        'num_infracoes': 1,
        'escore': 0.85  # Adiciona o score aqui
    }
    
    explicabilidade = {
        "idModelo": "RF-v2.1.3-TEST",
        "metodo": "SHAP",
        "contribuicoes": [
            {"feature": "velocidade", "valor": 120.5, "shap_value": 0.15},
            {"feature": "distancia", "valor": 50.2, "shap_value": 0.08}
        ],
        "janela": 999,
        "timestamp_calculo": "2024-01-01T12:00:00Z"
    }
    
    # Gera alerta de teste
    alerta = gerador.criar_alerta(
        passagem=par_info,
        explicabilidade=explicabilidade
    )
    
    print("✅ Alerta criado com sucesso!")
    
    # Testa formatação para NDJSON (sem quebras de linha)
    json_compacto = GeradorAlertasSimples.to_json(alerta, indent=None)
    print(f"\n📋 JSON compacto (NDJSON):")
    print(f"   Comprimento: {len(json_compacto)} caracteres")
    print(f"   Quebras de linha: {json_compacto.count(chr(10))}")
    
    # Verifica se é JSON válido
    try:
        parsed = json.loads(json_compacto)
        print("✅ JSON válido!")
        print(f"   Campos principais: {list(parsed.keys())}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        return
    
    # Testa formatação para visualização (com quebras de linha)
    json_formatado = GeradorAlertasSimples.to_json(alerta, indent=2)
    print(f"\n📋 JSON formatado (visualização):")
    print(f"   Comprimento: {len(json_formatado)} caracteres")
    print(f"   Quebras de linha: {json_formatado.count(chr(10))}")
    
    # Salva exemplo em arquivo NDJSON
    with open("teste_alerta_formatacao.ndjson", "w", encoding="utf-8") as f:
        f.write(json_compacto + "\n")
    
    print("✅ Arquivo teste_alerta_formatacao.ndjson criado!")
    
    # Verifica leitura do arquivo
    try:
        with open("teste_alerta_formatacao.ndjson", "r", encoding="utf-8") as f:
            linha = f.readline().strip()
            
        parsed_from_file = json.loads(linha)
        print("✅ Arquivo lido e parseado com sucesso!")
        print(f"   Placa: {parsed_from_file['info']['parametrosPreditivos'][0]['valor']}")
        print(f"   Probabilidade: {parsed_from_file['info']['probabilidade']}")
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")

if __name__ == "__main__":
    teste_formatacao_json()
