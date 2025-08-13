#!/usr/bin/env python3
"""
Teste simples das correções na geração de alertas.
"""

import json
import pandas as pd

def teste_simples_alertas():
    """Teste rápido das correções implementadas."""
    
    print("🧪 Verificando correções implementadas...")
    
    # Verificar se existe um arquivo de alerta para análise
    arquivo_analise = "alertas_janela_007.ndjson"
    
    try:
        with open(arquivo_analise, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
            
        print(f"📁 Analisando arquivo: {arquivo_analise}")
        print(f"📊 Total de linhas: {len(linhas)}")
        
        if len(linhas) == 0:
            print("ℹ️ Arquivo vazio")
            return
            
        # Analisar os primeiros alertas
        alertas_unicos = set()
        explicabilidades = []
        coordenadas = []
        
        for i, linha in enumerate(linhas[:10]):  # Primeiros 10 alertas
            try:
                alerta = json.loads(linha.strip())
                
                # Verificar estrutura básica
                placa = alerta['info']['parametrosPreditivos'][0]['valor']
                prob = alerta['info']['probabilidade']
                explicabilidade = alerta['info']['explicabilidade']
                coords = alerta['area']['geometria']['coordenadas']
                
                # Coletar dados para análise
                chave_alerta = f"{placa}_{coords[0]}_{coords[1]}_{alerta['timestampEmissao']}"
                alertas_unicos.add(chave_alerta)
                explicabilidades.append(explicabilidade['metodo'])
                coordenadas.append((coords[0], coords[1]))
                
                if i < 3:  # Mostrar detalhes dos primeiros 3
                    print(f"\n📋 Alerta {i+1}:")
                    print(f"  - Placa: {placa}")
                    print(f"  - Probabilidade: {prob}")
                    print(f"  - Explicabilidade: {explicabilidade['metodo']}")
                    print(f"  - Coordenadas: ({coords[0]:.6f}, {coords[1]:.6f})")
                    print(f"  - Features analisadas: {len(explicabilidade.get('contribuicoes', []))}")
                    
            except Exception as e:
                print(f"❌ Erro ao analisar linha {i+1}: {e}")
        
        # Estatísticas
        print(f"\n📊 Estatísticas dos primeiros 10 alertas:")
        print(f"  - Alertas únicos: {len(alertas_unicos)}")
        print(f"  - Possíveis duplicações: {10 - len(alertas_unicos)}")
        print(f"  - Métodos de explicabilidade: {set(explicabilidades)}")
        
        # Verificar se coordenadas são distintas
        coords_unicas = len(set(coordenadas))
        print(f"  - Coordenadas únicas: {coords_unicas}/10")
        
        if coords_unicas < 10:
            print("⚠️ Possível problema: muitas coordenadas iguais")
        
        # Verificar se ainda há problemas
        problemas = []
        if 10 - len(alertas_unicos) > 0:
            problemas.append(f"{10 - len(alertas_unicos)} possíveis duplicações")
        if "Feature Importance" in explicabilidades and "SHAP" in explicabilidades:
            problemas.append("métodos de explicabilidade misturados")
        if coords_unicas < 5:
            problemas.append("coordenadas muito repetitivas")
            
        if problemas:
            print(f"\n⚠️ Problemas identificados:")
            for problema in problemas:
                print(f"  - {problema}")
        else:
            print(f"\n✅ Nenhum problema obvio detectado nos primeiros 10 alertas")
            
    except FileNotFoundError:
        print(f"❌ Arquivo {arquivo_analise} não encontrado")
        return
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {e}")
        return

def verificar_correcoes_implementadas():
    """Verifica se as correções estão no código."""
    
    print("\n🔍 Verificando se correções estão implementadas...")
    
    try:
        with open('validacao_modelo_conceitual.py', 'r', encoding='utf-8') as f:
            codigo = f.read()
            
        correcoes = [
            ('datetime import', 'from datetime import datetime, timezone'),
            ('deduplicação', 'ids_processados = set()'),
            ('chave_conteudo', 'chave_conteudo ='),
            ('alertas_unicos', 'alertas_unicos = []'),
            ('SHAP timestamp', 'timestamp_calculo')
        ]
        
        for nome, padrao in correcoes:
            if padrao in codigo:
                print(f"  ✅ {nome}: implementado")
            else:
                print(f"  ❌ {nome}: não encontrado")
                
    except Exception as e:
        print(f"❌ Erro ao verificar código: {e}")

if __name__ == "__main__":
    teste_simples_alertas()
    verificar_correcoes_implementadas()
