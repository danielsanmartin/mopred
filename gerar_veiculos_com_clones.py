"""
Script para gerar um novo conjunto de veículos com clones reais.
"""

from gerador_veiculos import GeradorVeiculos

def main():
    print("🚀 GERANDO VEÍCULOS COM CLONES REAIS")
    print("=" * 50)
    
    # Carregar configurações do config.json
    import json
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Criar gerador
    gerador = GeradorVeiculos()
    
    # Usar configurações do config.json
    gerador.total_veiculos = config.get("total_veiculos", 1000)
    gerador.percentual_clonados = config.get("percentual_veiculos_clonados", 0.05)
    
    print(f"📋 Configurações do config.json:")
    print(f"   Total de veículos: {gerador.total_veiculos:,}")
    print(f"   Percentual de clonados: {gerador.percentual_clonados:.1%}")
    
    # Gerar veículos
    df = gerador.gerar_conjunto_veiculos()
    
    # Salvar
    gerador.salvar_csv(df, "veiculos_gerados_com_clones.csv")
    
    # Verificar clones
    print("\n🔍 VERIFICANDO CLONES GERADOS:")
    clonados = df[df['clonado'] == 1]
    placas_clonadas = clonados['placa'].value_counts()
    
    print(f"Total de veículos clonados: {len(clonados)}")
    print(f"Placas clonadas únicas: {len(placas_clonadas)}")
    print(f"Placas com múltiplas versões: {sum(placas_clonadas > 1)}")
    
    print("\nPrimeiras 10 placas clonadas:")
    for placa, count in placas_clonadas.head(10).items():
        placa_data = clonados[clonados['placa'] == placa]
        print(f"  {placa}: {count} versões")
        for idx, veiculo in placa_data.iterrows():
            print(f"    - {veiculo['marca']} {veiculo['modelo']} ({veiculo['tipo']}) {veiculo['cor']}")

if __name__ == "__main__":
    main()
