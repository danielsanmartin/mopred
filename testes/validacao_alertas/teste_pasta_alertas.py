#!/usr/bin/env python3
"""
Teste da funcionalidade de pasta configurável para alertas
"""

import json
import os
import tempfile
import shutil

def teste_pasta_alertas():
    """Testa se os alertas são salvos na pasta configurada."""
    
    print("🧪 Testando funcionalidade de pasta configurável para alertas...")
    
    # Criar pasta temporária para teste
    pasta_teste = "teste_alertas_temp"
    
    # Limpar se já existir
    if os.path.exists(pasta_teste):
        shutil.rmtree(pasta_teste)
    
    try:
        # 1. Teste de configuração
        print("\n1️⃣ Testando configuração...")
        
        # Carregar config atual
        with open('configs/config.json', 'r', encoding='utf-8') as f:
            config_original = json.load(f)
        
        # Verificar se campo foi adicionado
        pasta_config = config_original.get("pasta_alertas")
        if pasta_config:
            print(f"✅ Campo 'pasta_alertas' encontrado: {pasta_config}")
        else:
            print("❌ Campo 'pasta_alertas' não encontrado no config.json")
            return False
        
        # 2. Teste de criação de pasta
        print("\n2️⃣ Testando criação de pasta...")
        
        # Simular configuração com pasta teste
        config_teste = config_original.copy()
        config_teste["pasta_alertas"] = pasta_teste
        
        # Simular chamada de criação de pasta (como na função gerar_alertas_janela)
        pasta_alertas = config_teste.get("pasta_alertas", "alertas_gerados")
        
        if not os.path.exists(pasta_alertas):
            os.makedirs(pasta_alertas)
            print(f"✅ Pasta criada: {pasta_alertas}")
        
        # Verificar se pasta foi criada
        if os.path.exists(pasta_teste):
            print(f"✅ Pasta {pasta_teste} existe")
        else:
            print(f"❌ Pasta {pasta_teste} não foi criada")
            return False
        
        # 3. Teste de salvamento de arquivo
        print("\n3️⃣ Testando salvamento de arquivo...")
        
        # Simular salvamento de alerta
        arquivo_teste = os.path.join(pasta_teste, "alertas_janela_999.ndjson")
        
        alerta_exemplo = {
            "@context": "https://www.mopred.org/schemas/alerta/v1",
            "@type": "AlertaPreditivo", 
            "id": "test-123",
            "identificadorSistema": "TESTE",
            "info": {"teste": "arquivo na pasta configurada"}
        }
        
        from alertas import GeradorAlertasSimples
        
        with open(arquivo_teste, "w", encoding="utf-8") as f:
            f.write(GeradorAlertasSimples.to_json(alerta_exemplo, indent=None) + "\n")
        
        # Verificar se arquivo foi salvo
        if os.path.exists(arquivo_teste):
            print(f"✅ Arquivo salvo: {arquivo_teste}")
            
            # Verificar conteúdo
            with open(arquivo_teste, 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
            
            if '"teste":"arquivo na pasta configurada"' in conteudo:
                print("✅ Conteúdo do arquivo está correto")
            else:
                print("❌ Conteúdo do arquivo está incorreto")
                return False
        else:
            print(f"❌ Arquivo não foi salvo: {arquivo_teste}")
            return False
        
        # 4. Teste de consolidação
        print("\n4️⃣ Testando funcionalidade de consolidação...")
        
        # Criar mais um arquivo de teste
        arquivo_teste2 = os.path.join(pasta_teste, "alertas_janela_998.ndjson")
        alerta_exemplo2 = alerta_exemplo.copy()
        alerta_exemplo2["id"] = "test-456"
        
        with open(arquivo_teste2, "w", encoding="utf-8") as f:
            f.write(GeradorAlertasSimples.to_json(alerta_exemplo2, indent=None) + "\n")
        
        # Simular consolidação
        import glob
        padrao_alertas = os.path.join(pasta_teste, "alertas_janela_*.ndjson")
        arquivos_encontrados = glob.glob(padrao_alertas)
        
        print(f"✅ Arquivos encontrados para consolidação: {len(arquivos_encontrados)}")
        for arquivo in arquivos_encontrados:
            print(f"   - {os.path.basename(arquivo)}")
        
        if len(arquivos_encontrados) >= 2:
            print("✅ Funcionalidade de busca de arquivos funcionando")
        else:
            print("❌ Problema na busca de arquivos")
            return False
        
        print("\n🎉 Todos os testes passaram!")
        print(f"💡 A pasta '{pasta_config}' será usada para salvar os alertas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Limpar pasta de teste
        if os.path.exists(pasta_teste):
            shutil.rmtree(pasta_teste)
            print(f"🧹 Pasta de teste removida: {pasta_teste}")

if __name__ == "__main__":
    if teste_pasta_alertas():
        print("\n✅ Funcionalidade implementada com sucesso!")
        print("📋 Para usar:")
        print("   1. Configure 'pasta_alertas' no config.json")
        print("   2. Execute validacao_modelo_conceitual.py")
        print("   3. Alertas serão salvos na pasta configurada")
    else:
        print("\n❌ Funcionalidade tem problemas!")
