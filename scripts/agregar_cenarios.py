import json, os, glob
from pathlib import Path
import numpy as np
import pandas as pd

RUNS = Path("runs")  # cada subpasta: V10k_P1_S42, etc.
OUT = RUNS / "agregado"
OUT.mkdir(parents=True, exist_ok=True)

METRICAS = ["F1", "AUCPR", "Brier", "Accuracy"]  # ajusta conforme CSV
MODELOS = ["Tradicional", "Trad+Multi", "Adaptativo", "Adapt+Multi"]  # ajusta mapeamento

def _bootstrap_ci(vals, n_boot=2000, alpha=0.05, seed=42):
    vals = np.asarray(vals, dtype=float)
    vals = vals[~np.isnan(vals)]
    if vals.size == 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    means = [rng.choice(vals, size=vals.size, replace=True).mean() for _ in range(n_boot)]
    lo = float(np.percentile(means, 100 * (alpha/2)))
    hi = float(np.percentile(means, 100 * (1 - alpha/2)))
    return lo, hi

def _parse_id(run_id: str):
    # Ex.: V10k_P1_S42 → escala=10000, prev=0.01, seed=42
    parts = run_id.split("_")
    escala = int(parts[0][1:-1]) * 1000
    prev = float(parts[1][1:]) / 100.0
    seed = int(parts[2][1:])
    return escala, prev, seed

def _map_modelo(row):
    # tente mapear a coluna 'tipo' ou 'modelo' para nomes padronizados
    if "tipo" in row:
        t = row["tipo"]
        mapa = {
            "tradicional": "Tradicional",
            "tradicional_multimodal": "Trad+Multi",
            "adaptativo": "Adaptativo",
            "adaptativo_multimodal": "Adapt+Multi",
        }
        return mapa.get(str(t).lower(), str(t))
    return row.get("modelo", "Modelo")

def coletar_resumo_runs():
    linhas = []
    for run_dir in sorted([p for p in RUNS.iterdir() if p.is_dir() and "_" in p.name]):
        rid = run_dir.name
        escala, prev, seed = _parse_id(rid)
        csv_path = run_dir / "csvs" / "comparacao_modelos_resultados.csv"
        if not csv_path.exists():
            continue
        df = pd.read_csv(csv_path)
        # normalizar nomes de colunas (case-insensitive)
        cols = {c.lower(): c for c in df.columns}
        # métricas por janela → média por modelo na execução
        if "janela" not in df.columns:
            continue
        # adicionar coluna 'modelo_padrao'
        df["modelo_padrao"] = df.apply(_map_modelo, axis=1)
        for modelo, g in df.groupby("modelo_padrao"):
            linha = {
                "run_id": rid, "escala": escala, "prevalencia": prev, "seed": seed, "modelo": modelo
            }
            for met in METRICAS:
                # Mapear nomes das métricas para as colunas reais do CSV
                col_map = {
                    "F1": "f1",
                    "AUCPR": "auprc", 
                    "Brier": "brier",
                    "Accuracy": "accuracy"
                }
                col_name = col_map.get(met, met.lower())
                
                if col_name in g.columns:
                    vals = g[col_name].values
                else:
                    vals = np.array([])
                linha[met] = float(np.nanmean(vals)) if vals.size else np.nan
            linhas.append(linha)
    df_runs = pd.DataFrame(linhas)
    df_runs.to_csv(OUT / "runs_summary.csv", index=False, encoding="utf-8")
    return df_runs

def agregar_por_cenario(df_runs: pd.DataFrame):
    # agrega por (escala, prevalencia, modelo) ao longo das seeds
    rows = []
    for (escala, prev, modelo), g in df_runs.groupby(["escala", "prevalencia", "modelo"]):
        row = {"escala": escala, "prevalencia": prev, "modelo": modelo, "n_seeds": g["seed"].nunique()}
        for met in METRICAS:
            vals = g[met].values
            row[met + "_mean"] = float(np.nanmean(vals)) if vals.size else np.nan
            lo, hi = _bootstrap_ci(vals, n_boot=2000, alpha=0.05, seed=42) if vals.size else (np.nan, np.nan)
            row[met + "_lo95"] = lo
            row[met + "_hi95"] = hi
        rows.append(row)
    df_cenarios = pd.DataFrame(rows)
    df_cenarios = df_cenarios.sort_values(["escala", "prevalencia", "modelo"])
    df_cenarios.to_csv(OUT / "cenarios_summary.csv", index=False, encoding="utf-8")
    return df_cenarios

def gerar_tabela_latex(df_cenarios: pd.DataFrame, metrica="AUCPR"):
    # pivot: linhas = escala, colunas = (prevalencia, modelo)
    piv = df_cenarios.pivot_table(index="escala", columns=["prevalencia", "modelo"],
                                  values=f"{metrica}_mean", aggfunc="first")
    latex = piv.to_latex(na_rep="–", float_format="%.3f", multirow=True, multicolumn=True, escape=False)
    (OUT / f"tabela_{metrica.lower()}.tex").write_text(latex, encoding="utf-8")

def verificar_dados_suficientes(df_cenarios):
    print("\n🔍 VERIFICANDO DADOS PARA HEATMAPS:")
    for met in ["AUCPR", "F1"]:
        dados_validos = df_cenarios[f"{met}_mean"].dropna()
        print(f"   {met}: {len(dados_validos)}/{len(df_cenarios)} cenários têm dados")
        if len(dados_validos) < 4:  # precisa de pelo menos 4 pontos para heatmap
            print(f"   ⚠️ {met}: dados insuficientes para heatmap")
    return True

def gerar_heatmaps_delta(df_cenarios: pd.DataFrame):
    print("\n🔍 VERIFICANDO DADOS PARA HEATMAPS:")
    dados_suficientes = False
    for met in ["AUCPR", "F1"]:
        dados_validos = df_cenarios[f"{met}_mean"].dropna()
        print(f"   {met}: {len(dados_validos)}/{len(df_cenarios)} cenários têm dados")
        if len(dados_validos) >= 4:  # precisa de pelo menos 4 pontos para heatmap
            dados_suficientes = True
        else:
            print(f"   ⚠️ {met}: dados insuficientes para heatmap")
    
    if not dados_suficientes:
        print("   ❌ Pulando heatmaps - dados insuficientes")
        return
    
    # Δ Adapt − Trad e Δ (…+Multi − …) por (escala, prevalencia)
    import matplotlib.pyplot as plt
    import seaborn as sns
    def pick(df, modelo, met):
        m = df[df["modelo"]==modelo].set_index(["escala","prevalencia"])[f"{met}_mean"]
        return m
    for met in ["AUCPR", "F1"]:
        a = pick(df_cenarios, "Adaptativo", met)
        t = pick(df_cenarios, "Tradicional", met)
        am = pick(df_cenarios, "Adapt+Multi", met)
        tm = pick(df_cenarios, "Trad+Multi", met)
        delta_adapt_trad = (a - t).unstack("prevalencia")
        delta_multi_trad = (tm - t).unstack("prevalencia")
        delta_multi_adapt = (am - a).unstack("prevalencia")
        for name, mat in [("delta_adapt_minus_trad", delta_adapt_trad),
                          ("delta_multi_trad", delta_multi_trad),
                          ("delta_multi_adapt", delta_multi_adapt)]:
            plt.figure(figsize=(6,3))
            sns.heatmap(mat.sort_index(), annot=True, fmt=".3f", cmap="RdBu", center=0)
            plt.title(f"{name} ({met})")
            plt.ylabel("Escala"); plt.xlabel("Prevalência")
            plt.tight_layout()
            plt.savefig(OUT / f"heatmap_{name}_{met.lower()}.png", dpi=150)
            plt.close()

if __name__ == "__main__":
    df_runs = coletar_resumo_runs()
    df_cenarios = agregar_por_cenario(df_runs)
    gerar_tabela_latex(df_cenarios, metrica="AUCPR")
    gerar_tabela_latex(df_cenarios, metrica="F1")
    gerar_heatmaps_delta(df_cenarios)
    print("✅ Agregados em runs/agregado/*.csv e figuras geradas.")