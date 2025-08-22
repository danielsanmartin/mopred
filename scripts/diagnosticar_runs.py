import json, os
from pathlib import Path
import pandas as pd

RUNS = Path("runs")

def diagnosticar_runs():
    print("🔍 DIAGNÓSTICO DOS CENÁRIOS:")
    print("=" * 50)
    
    cenarios_encontrados = []
    cenarios_com_csv = []
    cenarios_com_dados = []
    
    for run_dir in sorted([p for p in RUNS.iterdir() if p.is_dir() and "_" in p.name]):
        rid = run_dir.name
        cenarios_encontrados.append(rid)
        
        csv_path = run_dir / "csvs" / "comparacao_modelos_resultados.csv"
        config_path = run_dir / "config" / "config.json"
        
        # Verifica arquivos
        has_csv = csv_path.exists()
        has_config = config_path.exists()
        
        print(f"\n📁 {rid}:")
        print(f"   Config: {'✅' if has_config else '❌'}")
        print(f"   CSV: {'✅' if has_csv else '❌'}")
        
        if has_csv:
            cenarios_com_csv.append(rid)
            try:
                df = pd.read_csv(csv_path)
                print(f"   Linhas: {len(df)}")
                print(f"   Colunas: {list(df.columns)}")
                
                if len(df) > 0:
                    cenarios_com_dados.append(rid)
                    # Mostra sample das métricas
                    metrics = ['F1', 'AUCPR', 'Brier', 'Accuracy']
                    for m in metrics:
                        if m in df.columns:
                            vals = df[m].dropna()
                            if len(vals) > 0:
                                print(f"   {m}: {vals.mean():.3f} ± {vals.std():.3f} (n={len(vals)})")
                            else:
                                print(f"   {m}: todos NaN")
                else:
                    print(f"   ⚠️ CSV vazio")
                    
            except Exception as e:
                print(f"   ❌ Erro lendo CSV: {e}")
    
    print(f"\n📊 RESUMO:")
    print(f"   Cenários encontrados: {len(cenarios_encontrados)}")
    print(f"   Com CSV: {len(cenarios_com_csv)}")
    print(f"   Com dados: {len(cenarios_com_dados)}")
    
    if len(cenarios_com_dados) == 0:
        print(f"\n❌ PROBLEMA: Nenhum cenário tem dados válidos!")
        print(f"   Possíveis causas:")
        print(f"   • Execução paralela falhou em todos os cenários")
        print(f"   • CSV gerado mas vazio (sem métricas)")
        print(f"   • Problema no comparador_modelos.py")
    
    return cenarios_encontrados, cenarios_com_csv, cenarios_com_dados

if __name__ == "__main__":
    diagnosticar_runs()