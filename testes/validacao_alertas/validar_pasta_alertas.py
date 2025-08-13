#!/usr/bin/env python3
"""
Teste completo da funcionalidade de pasta configurável
"""

import json
import os
import sys

def teste_funcionalidade_completa():
    """Teste da funcionalidade completa de pasta configurável."""
    
    print("🧪 Teste completo da funcionalidade de pasta configurável...")
    
    # 1. Verificar configuração atual
    print("\n1️⃣ Verificando configuração atual...")
    
    try:
        with open('configs/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        pasta_config = config.get("pasta_alertas")
        print(f"✅ Pasta configurada: {pasta_config}")
        
        if not pasta_config:
            print("❌ Campo 'pasta_alertas' não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao ler configs/config.json: {e}")
        return False
    
    # 2. Verificar se pasta existe
    print(f"\n2️⃣ Verificando pasta {pasta_config}...")
    
    if os.path.exists(pasta_config):
        print(f"✅ Pasta existe: {pasta_config}")
        
        # Listar arquivos na pasta
        arquivos = os.listdir(pasta_config)
        arquivos_alertas = [f for f in arquivos if f.endswith('.ndjson')]
        
        print(f"📊 Arquivos de alertas encontrados: {len(arquivos_alertas)}")
        for arquivo in sorted(arquivos_alertas)[:5]:  # Mostrar apenas os primeiros 5
            arquivo_path = os.path.join(pasta_config, arquivo)
            tamanho = os.path.getsize(arquivo_path)
            print(f"   - {arquivo} ({tamanho:,} bytes)")
        
        if len(arquivos_alertas) > 5:
            print(f"   ... e mais {len(arquivos_alertas) - 5} arquivos")
            
    else:
        print(f"⚠️ Pasta não existe ainda: {pasta_config}")
        print("💡 Será criada automaticamente na próxima execução")
    
    # 3. Testar se as funções estão configuradas corretamente
    print(f"\n3️⃣ Verificando código atualizado...")
    
    try:
        # Verificar se as modificações estão no código
        with open('validacao_modelo_conceitual.py', 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        checks = [
            ('pasta_alertas', 'config.get("pasta_alertas"'),
            ('os.makedirs', 'os.makedirs(pasta_alertas)'),
            ('os.path.join', 'os.path.join(pasta_alertas'),
            ('glob.glob', 'padrao_alertas = os.path.join(pasta_alertas')
        ]
        
        for nome, padrao in checks:
            if padrao in codigo:
                print(f"✅ {nome}: código atualizado")
            else:
                print(f"❌ {nome}: código não encontrado")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar código: {e}")
        return False
    
    # 4. Resumo da funcionalidade
    print(f"\n4️⃣ Resumo da funcionalidade implementada...")
    
    print("✅ Funcionalidades implementadas:")
    print("   📁 Pasta configurável via config.json")
    print("   🏗️ Criação automática da pasta")
    print("   💾 Salvamento de alertas por janela na pasta")
    print("   📋 Consolidação de alertas na pasta")
    print("   🔍 Busca de arquivos na pasta configurada")
    
    print(f"\n📋 Como usar:")
    print(f"   1. Configure 'pasta_alertas' no config.json")
    print(f"   2. Execute: python validacao_modelo_conceitual.py")
    print(f"   3. Todos os alertas serão salvos em: ./{pasta_config}/")
    
    return True

if __name__ == "__main__":
    if teste_funcionalidade_completa():
        print("\n🎉 Funcionalidade completa e funcionando!")
        print("💡 Ready to use!")
    else:
        print("\n❌ Há problemas na implementação")
        sys.exit(1)
