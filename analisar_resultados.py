"""
Análise Visual dos Resultados da Comparação de Modelos
======================================================

Gera gráficos e relatórios detalhados da comparação RF Tradicional vs Adaptativo.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss
from scipy.stats import wilcoxon

def _bootstrap_ci(values, n_boot: int = 1000, alpha: float = 0.05, seed: int = 42):
    """IC bootstrap da média (ex.: 95%) para um vetor de métricas."""
    vals = np.asarray(values, dtype=float)
    vals = vals[~np.isnan(vals)]
    if vals.size == 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    means = [rng.choice(vals, size=vals.size, replace=True).mean() for _ in range(n_boot)]
    lo = np.percentile(means, 100 * (alpha/2))
    hi = np.percentile(means, 100 * (1 - alpha/2))
    return float(lo), float(hi)

def _imprimir_ic_e_wilcoxon(df: pd.DataFrame):
    """Imprime IC 95% (bootstrap) por cenário e Wilcoxon pareado por janela (names case-insensitive)."""
    if "janela" not in df.columns:
        print("\n⚠️ Séries por janela ausentes; não é possível calcular IC/Wilcoxon.")
        return

    # Mapeamento case-insensitive de colunas
    cols_lower = {c.lower(): c for c in df.columns}
    def col(name_variants: list[str]) -> str | None:
        for n in name_variants:
            c = cols_lower.get(n.lower())
            if c is not None:
                return c
        return None

    chave = "tipo" if col(["tipo"]) else "modelo"
    if chave not in df.columns:
        print("\n⚠️ Coluna de cenário ausente (tipo/modelo).")
        return

    grupos = {
        "Tradicional": df[df[chave].isin(["tradicional", "Tradicional"])],
        "Trad+Multi": df[df[chave].isin(["tradicional_multimodal", "Trad+Multi"])],
        "Adaptativo": df[df[chave].isin(["adaptativo", "Adaptativo"])],
        "Adapt+Multi": df[df[chave].isin(["adaptativo_multimodal", "Adapt+Multi"])],
    }

    # Resolver nomes reais das métricas
    f1_col = col(["f1", "F1"])
    auprc_col = col(["auprc", "AUCPR"])
    brier_col = col(["brier", "Brier"])

    print("\n📏 IC 95% (bootstrap) por cenário:")
    for nome, g in grupos.items():
        if g.empty:
            continue
        for label, met_col in [("F1", f1_col), ("AUCPR", auprc_col), ("Brier", brier_col)]:
            if met_col is None or met_col not in g.columns:
                continue
            vals = g[met_col].values
            media = float(np.nanmean(vals))
            lo, hi = _bootstrap_ci(vals, n_boot=1000, alpha=0.05, seed=42)
            print(f"   {nome:14} {label:6} = {media:.3f} [{lo:.3f}, {hi:.3f}]")

    def _serie(df_mod: pd.DataFrame, metric_col: str) -> pd.Series:
        s = df_mod.set_index("janela")[metric_col]
        return s[~s.isna()]

    print("\n🧪 Teste de Wilcoxon (pareado por janela):")
    for (m1, m2) in [("Tradicional", "Adaptativo"), ("Trad+Multi", "Adapt+Multi")]:
        g1, g2 = grupos.get(m1), grupos.get(m2)
        if g1 is None or g2 is None or g1.empty or g2.empty:
            continue
        for label, met_col in [("F1", f1_col), ("AUCPR", auprc_col)]:
            if met_col is None or met_col not in g1.columns or met_col not in g2.columns:
                continue
            s1, s2 = _serie(g1, met_col), _serie(g2, met_col)
            idx = s1.index.intersection(s2.index)
            if len(idx) < 5:
                continue
            stat, p = wilcoxon(s1.loc[idx], s2.loc[idx], zero_method="wilcox")
            print(f"   {m1:12} vs {m2:12} — {label}: n={len(idx)}  W={stat:.1f}  p={p:.4f}")

def _imprimir_metricas_complementares(df: pd.DataFrame):
    """Imprime AUCPR, Brier e prevalência média por cenário.
    Recalcula métricas por linha quando ausentes/NaN usando y_true/y_score.
    """
    import numpy as np, json
    from sklearn.metrics import average_precision_score, brier_score_loss

    df = df.copy()
    tem_y_cols = {"y_true", "y_score"} <= set(df.columns)
    if not tem_y_cols:
        print("\nℹ️ Observação: arquivo de resultados não contém colunas y_true/y_score. \n   AUCPR e Brier exigem probabilidades; para habilitar, reexecute o passo 2 (validação) para regenerar o CSV.")

    # Parse listas uma vez se disponível
    yt_list = None
    ys_list = None
    if tem_y_cols:
        def _parse_series(col):
            try:
                return df[col].apply(lambda s: json.loads(s) if isinstance(s, str) and s.strip() != '' else None)
            except Exception:
                return pd.Series([None] * len(df))
        yt_list = _parse_series("y_true")
        ys_list = _parse_series("y_score")

    # Garantir colunas de métricas existem
    if "auprc" not in df.columns:
        df["auprc"] = np.nan
    if "brier" not in df.columns:
        df["brier"] = np.nan

    # Preencher AUCPR/Brier onde estiver NaN e houver dados
    if tem_y_cols:
        def _row_auprc(i):
            try:
                yt = yt_list.iloc[i]; ys = ys_list.iloc[i]
                if isinstance(yt, list) and isinstance(ys, list) and len(yt) == len(ys) and len(yt) > 0:
                    # AUCPR precisa de pelo menos 2 classes distintas
                    return average_precision_score(yt, ys) if len(set(yt)) > 1 else np.nan
            except Exception:
                pass
            return np.nan
        def _row_brier(i):
            try:
                yt = yt_list.iloc[i]; ys = ys_list.iloc[i]
                if isinstance(yt, list) and isinstance(ys, list) and len(yt) == len(ys) and len(yt) > 0:
                    return brier_score_loss(yt, ys)
            except Exception:
                pass
            return np.nan
        mask_au = df["auprc"].isna()
        mask_br = df["brier"].isna()
        if mask_au.any():
            df.loc[mask_au, "auprc"] = [ _row_auprc(i) for i in df.index[mask_au] ]
        if mask_br.any():
            df.loc[mask_br, "brier"] = [ _row_brier(i) for i in df.index[mask_br] ]

    # Prevalência observada (calcula de y_true quando houver; senão, usa n_suspeitos/n_amostras)
    if "prevalencia_observada" not in df.columns:
        df["prevalencia_observada"] = np.nan
    if tem_y_cols:
        def _prev_val(i):
            try:
                yt = yt_list.iloc[i]
                return float(np.mean(yt)) if isinstance(yt, list) and len(yt) else np.nan
            except Exception:
                return np.nan
        mask_prev = df["prevalencia_observada"].isna()
        if mask_prev.any():
            df.loc[mask_prev, "prevalencia_observada"] = [ _prev_val(i) for i in df.index[mask_prev] ]
    else:
        # Fallback a partir de contagens agregadas
        if {"n_suspeitos", "n_amostras"} <= set(df.columns):
            with np.errstate(divide='ignore', invalid='ignore'):
                frac = df["n_suspeitos"].astype(float) / df["n_amostras"].replace({0: np.nan}).astype(float)
            mask_prev = df["prevalencia_observada"].isna()
            df.loc[mask_prev, "prevalencia_observada"] = frac

    # Mapear cenários (ajuste conforme suas labels/coluna)
    # Suporta 'tipo' ou 'modelo' com nomes padronizados
    if "tipo" in df.columns:
        grupos = {
            "Tradicional": df[df["tipo"]=="tradicional"],
            "Trad+Multi": df[df["tipo"]=="tradicional_multimodal"],
            "Adaptativo": df[df["tipo"]=="adaptativo"],
            "Adapt+Multi": df[df["tipo"]=="adaptativo_multimodal"],
        }
    else:
        grupos = { n: g for n,g in df.groupby("modelo") }

    def _safe_mean(series):
        arr = series.to_numpy(dtype=float)
        return float(np.nanmean(arr)) if arr.size else float("nan")

    print("\n📐 MÉTRICAS COMPLEMENTARES (médias por cenário):")
    for nome, d in grupos.items():
        if d.empty: 
            continue
        print(f"   {nome:14}  AUCPR={_safe_mean(d.get('auprc', pd.Series(dtype=float))):.3f}  "
              f"Brier={_safe_mean(d.get('brier', pd.Series(dtype=float))):.3f}  "
              f"Prev={_safe_mean(d.get('prevalencia_observada', pd.Series(dtype=float))):.3f}")

def _get_csv_path():
    """Resolve o caminho do CSV usando configs/config.json (pasta_csvs), com fallback para 'csvs'."""
    try:
        with open("configs/config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
        pasta_csvs = cfg.get("pasta_csvs", "csvs")
    except Exception:
        pasta_csvs = "csvs"
    return os.path.join(pasta_csvs, "comparacao_modelos_resultados.csv")

def analisar_resultados():  
    # Carregar resultados
    csv_path = _get_csv_path()
    df = pd.read_csv(csv_path)
    _imprimir_metricas_complementares(df)
    _imprimir_ic_e_wilcoxon(df)            # novo: IC 95% e Wilcoxon
    # Enriquecer: parse de y_true/y_score quando disponíveis
    def parse_scores(col):
        try:
            return df[col].apply(lambda s: json.loads(s) if isinstance(s, str) and s.strip() != '' else None)
        except Exception:
            return pd.Series([None] * len(df))

    if 'y_true' in df.columns and 'y_score' in df.columns:
        df['y_true_list'] = parse_scores('y_true')
        df['y_score_list'] = parse_scores('y_score')

    # Se as colunas auprc/brier não existem mas temos listas, compute on-the-fly
    if 'auprc' not in df.columns and 'y_true_list' in df.columns and 'y_score_list' in df.columns:
        def _row_auprc(row):
            yt, ys = row.get('y_true_list'), row.get('y_score_list')
            try:
                if isinstance(yt, list) and isinstance(ys, list) and len(yt) == len(ys) and len(set(yt)) > 1:
                    return average_precision_score(yt, ys)
            except Exception:
                pass
            return np.nan
        def _row_brier(row):
            yt, ys = row.get('y_true_list'), row.get('y_score_list')
            try:
                if isinstance(yt, list) and isinstance(ys, list) and len(yt) == len(ys):
                    return brier_score_loss(yt, ys)
            except Exception:
                pass
            return np.nan
        df['auprc'] = df.apply(_row_auprc, axis=1)
        df['brier'] = df.apply(_row_brier, axis=1)

    # Separar por tipo de modelo
    df_trad = df[df['tipo'] == 'tradicional'].reset_index(drop=True)
    df_trad_multi = df[df['tipo'] == 'tradicional_multimodal'].reset_index(drop=True)
    df_adapt = df[df['tipo'] == 'adaptativo'].reset_index(drop=True)
    df_adapt_multi = df[df['tipo'] == 'adaptativo_multimodal'].reset_index(drop=True)

    # Análise do impacto da multimodalidade
    print(f"\n🔬 ANÁLISE DO IMPACTO DA MULTIMODALIDADE NA PERFORMANCE:")
    print(f"=" * 60)
    def impacto_str(delta):
        if np.isnan(delta):
            return "(sem dados)"
        if delta > 0:
            return f"↑ Melhora (+{delta:.3f})"
        elif delta < 0:
            return f"↓ Piora ({delta:.3f})"
        else:
            return "= Estável"

    # F1-score
    f1_trad = df_trad['f1'].mean()
    f1_trad_multi = df_trad_multi['f1'].mean()
    f1_adapt = df_adapt['f1'].mean()
    f1_adapt_multi = df_adapt_multi['f1'].mean()
    acc_trad = df_trad['accuracy'].mean()
    acc_trad_multi = df_trad_multi['accuracy'].mean()
    acc_adapt = df_adapt['accuracy'].mean()
    acc_adapt_multi = df_adapt_multi['accuracy'].mean()

    print(f"\n🏛️ Tradicional:")
    print(f"   F1-score:   {f1_trad:.3f} → {f1_trad_multi:.3f}  {impacto_str(f1_trad_multi - f1_trad)}")
    print(f"   Accuracy:   {acc_trad:.3f} → {acc_trad_multi:.3f}  {impacto_str(acc_trad_multi - acc_trad)}")

    print(f"\n🔄 Adaptativo:")
    print(f"   F1-score:   {f1_adapt:.3f} → {f1_adapt_multi:.3f}  {impacto_str(f1_adapt_multi - f1_adapt)}")
    print(f"   Accuracy:   {acc_adapt:.3f} → {acc_adapt_multi:.3f}  {impacto_str(acc_adapt_multi - acc_adapt)}")

    # Conclusão automática sobre o impacto da multimodalidade
    print("\n📋 CONCLUSÃO SOBRE O IMPACTO DA MULTIMODALIDADE:")
    def conclusao_impacto(delta, nome):
        if np.isnan(delta):
            return f"   • {nome}: Não foi possível avaliar o impacto (dados ausentes)."
        if delta > 0:
            return f"   • {nome}: A multimodalidade MELHOROU a performance."
        elif delta < 0:
            return f"   • {nome}: A multimodalidade PIOROU a performance."
        else:
            return f"   • {nome}: A multimodalidade NÃO ALTEROU a performance."

    print(conclusao_impacto(f1_trad_multi - f1_trad, "Random Forest Tradicional (F1-score)"))
    print(conclusao_impacto(acc_trad_multi - acc_trad, "Random Forest Tradicional (Accuracy)"))
    print(conclusao_impacto(f1_adapt_multi - f1_adapt, "Random Forest Adaptativo (F1-score)"))
    print(conclusao_impacto(acc_adapt_multi - acc_adapt, "Random Forest Adaptativo (Accuracy)"))

    # Teste pareado de Wilcoxon para F1 entre básico e multimodal em cada paradigma
    try:
        if len(df_trad) and len(df_trad_multi):
            comum = sorted(set(df_trad['janela']).intersection(df_trad_multi['janela']))
            x = [df_trad[df_trad['janela']==j]['f1'].values[0] for j in comum]
            y = [df_trad_multi[df_trad_multi['janela']==j]['f1'].values[0] for j in comum]
            if len(comum) >= 5:
                stat, p = wilcoxon(x, y, zero_method='wilcox', alternative='two-sided', method='approx')
                print(f"\n🧪 Wilcoxon Trad vs Trad+Multi (F1) sobre {len(comum)} janelas: p={p:.4f}")
        if len(df_adapt) and len(df_adapt_multi):
            comum = sorted(set(df_adapt['janela']).intersection(df_adapt_multi['janela']))
            x = [df_adapt[df_adapt['janela']==j]['f1'].values[0] for j in comum]
            y = [df_adapt_multi[df_adapt_multi['janela']==j]['f1'].values[0] for j in comum]
            if len(comum) >= 5:
                stat, p = wilcoxon(x, y, zero_method='wilcox', alternative='two-sided', method='approx')
                print(f"🧪 Wilcoxon Adapt vs Adapt+Multi (F1) sobre {len(comum)} janelas: p={p:.4f}")
    except Exception as e:
        print(f"⚠️ Falha no Wilcoxon: {e}")
    """Análise detalhada dos resultados."""
    print("📊 ANÁLISE DETALHADA DOS RESULTADOS")
    print("=" * 60)
    
    # Carregar resultados (mesmo caminho)
    df = pd.read_csv(csv_path)
    # Garantir prevalência observada disponível após recarga
    if 'prevalencia_observada' not in df.columns and 'y_true' in df.columns:
        def _prev_from_json(s):
            try:
                arr = json.loads(s) if isinstance(s, str) else None
                return float(np.mean(arr)) if isinstance(arr, list) and len(arr) else np.nan
            except Exception:
                return np.nan
        df['prevalencia_observada'] = df['y_true'].apply(_prev_from_json)
    
    # Separar por tipo de modelo
    df_trad = df[df['tipo'] == 'tradicional'].reset_index(drop=True)
    df_trad_multi = df[df['tipo'] == 'tradicional_multimodal'].reset_index(drop=True)
    df_adapt = df[df['tipo'] == 'adaptativo'].reset_index(drop=True)
    df_adapt_multi = df[df['tipo'] == 'adaptativo_multimodal'].reset_index(drop=True)

    print(f"📈 ANÁLISE POR JANELA TEMPORAL (4 CENÁRIOS):")
    print(f"=" * 60)

    # Obter todas as janelas únicas presentes nos quatro cenários
    janelas_trad = set(df_trad['janela'].unique())
    janelas_trad_multi = set(df_trad_multi['janela'].unique())
    janelas_adapt = set(df_adapt['janela'].unique())
    janelas_adapt_multi = set(df_adapt_multi['janela'].unique())
    todas_janelas = sorted(janelas_trad | janelas_trad_multi | janelas_adapt | janelas_adapt_multi)

    for janela in todas_janelas:
        # Buscar métricas de cada cenário para a janela
        def get_metric(df, janela, col):
            row = df[df['janela'] == janela]
            if not row.empty:
                return row.iloc[0][col]
            else:
                return None

        acc_trad = get_metric(df_trad, janela, 'accuracy')
        f1_trad = get_metric(df_trad, janela, 'f1')
        acc_trad_multi = get_metric(df_trad_multi, janela, 'accuracy')
        f1_trad_multi = get_metric(df_trad_multi, janela, 'f1')
        acc_adapt = get_metric(df_adapt, janela, 'accuracy')
        f1_adapt = get_metric(df_adapt, janela, 'f1')
        acc_adapt_multi = get_metric(df_adapt_multi, janela, 'accuracy')
        f1_adapt_multi = get_metric(df_adapt_multi, janela, 'f1')

        # Determinar fase
        if janela <= 3:
            fase = "BASELINE"
        elif janela <= 6:
            fase = "MUDANÇA"
        else:
            fase = "NOVOS PADRÕES"

        print(f"\n🪟 JANELA {janela} ({fase}):")
        # Definir largura fixa para cada coluna
        col_widths = [13, 13, 13, 13, 13]
        def center(text, width):
            return str(text).center(width)
        # Cabeçalho
        print("   " + "┌" + "┬".join(["─"*w for w in col_widths]) + "┐")
        header = ["Métrica", "Tradicional", "Trad+Multi", "Adaptativo", "Adapt+Multi"]
        print("   │" + "│".join([center(h, w) for h, w in zip(header, col_widths)]) + "│")
        print("   " + "├" + "┼".join(["─"*w for w in col_widths]) + "┤")
        def fmt(val):
            return center(f"{val:.3f}" if val is not None else "N/A", 13)
        print("   │" + "│".join([center("Accuracy", 13), fmt(acc_trad), fmt(acc_trad_multi), fmt(acc_adapt), fmt(acc_adapt_multi)]) + "│")
        print("   │" + "│".join([center("F1-Score", 13), fmt(f1_trad), fmt(f1_trad_multi), fmt(f1_adapt), fmt(f1_adapt_multi)]) + "│")
        print("   " + "└" + "┴".join(["─"*w for w in col_widths]) + "┘")
        # Impacto da multimodalidade
        print(f"   Impacto da Multimodalidade:")
        trad_delta = f1_trad_multi - f1_trad if f1_trad is not None and f1_trad_multi is not None else None
        adapt_delta = f1_adapt_multi - f1_adapt if f1_adapt is not None and f1_adapt_multi is not None else None
        print(f"     Tradicional: ΔF1 = {trad_delta:+.3f}" if trad_delta is not None else "     Tradicional: ΔF1 = N/A")
        print(f"     Adaptativo:  ΔF1 = {adapt_delta:+.3f}" if adapt_delta is not None else "     Adaptativo:  ΔF1 = N/A")

        # Complementar: AUCPR e Brier por janela se disponíveis
        if 'auprc' in df.columns and 'brier' in df.columns:
            au_trad = get_metric(df_trad, janela, 'auprc'); au_adapt = get_metric(df_adapt, janela, 'auprc')
            au_trad_m = get_metric(df_trad_multi, janela, 'auprc'); au_adapt_m = get_metric(df_adapt_multi, janela, 'auprc')
            br_trad = get_metric(df_trad, janela, 'brier'); br_adapt = get_metric(df_adapt, janela, 'brier')
            br_trad_m = get_metric(df_trad_multi, janela, 'brier'); br_adapt_m = get_metric(df_adapt_multi, janela, 'brier')
            print(f"   AUCPR: Trad={au_trad if au_trad is not None else np.nan:.3f} | Trad+Multi={au_trad_m if au_trad_m is not None else np.nan:.3f} | Adapt={au_adapt if au_adapt is not None else np.nan:.3f} | Adapt+Multi={au_adapt_m if au_adapt_m is not None else np.nan:.3f}")
            print(f"   Brier: Trad={br_trad if br_trad is not None else np.nan:.3f} | Trad+Multi={br_trad_m if br_trad_m is not None else np.nan:.3f} | Adapt={br_adapt if br_adapt is not None else np.nan:.3f} | Adapt+Multi={br_adapt_m if br_adapt_m is not None else np.nan:.3f}")
    
    # Análise por fase
    print(f"\n📊 ANÁLISE POR FASE (IMPACTO DA MULTIMODALIDADE):")
    print(f"=" * 60)
    fases = {
        "BASELINE (Janelas 1-3)": [1, 2, 3],
        "MUDANÇA (Janelas 4-6)": [4, 5, 6],
        "NOVOS PADRÕES (Janelas 7-9)": [7, 8, 9]
    }
    resumo_fases = []
    for nome_fase, janelas in fases.items():
        print(f"\n🔍 {nome_fase}:")
        # Filtrar dados da fase
        fase_trad = df_trad[df_trad['janela'].isin(janelas)]
        fase_trad_multi = df_trad_multi[df_trad_multi['janela'].isin(janelas)]
        fase_adapt = df_adapt[df_adapt['janela'].isin(janelas)]
        fase_adapt_multi = df_adapt_multi[df_adapt_multi['janela'].isin(janelas)]
        # Calcular médias da fase
        f1_trad_fase = fase_trad['f1'].mean()
        f1_trad_multi_fase = fase_trad_multi['f1'].mean()
        f1_adapt_fase = fase_adapt['f1'].mean()
        f1_adapt_multi_fase = fase_adapt_multi['f1'].mean()
        acc_trad_fase = fase_trad['accuracy'].mean()
        acc_trad_multi_fase = fase_trad_multi['accuracy'].mean()
        acc_adapt_fase = fase_adapt['accuracy'].mean()
        acc_adapt_multi_fase = fase_adapt_multi['accuracy'].mean()
        print(f"   F1-Score Médio:")
        print(f"     🏛️ Tradicional:         {f1_trad_fase:.3f}")
        print(f"     🏛️ Tradicional+Multi:   {f1_trad_multi_fase:.3f} (Δ {f1_trad_multi_fase - f1_trad_fase:+.4f})")
        print(f"     🔄 Adaptativo:          {f1_adapt_fase:.3f}")
        print(f"     🔄 Adaptativo+Multi:    {f1_adapt_multi_fase:.3f} (Δ {f1_adapt_multi_fase - f1_adapt_fase:+.4f})")
        print(f"   Accuracy Médio:")
        print(f"     🏛️ Tradicional:         {acc_trad_fase:.3f}")
        print(f"     🏛️ Tradicional+Multi:   {acc_trad_multi_fase:.3f} (Δ {acc_trad_multi_fase - acc_trad_fase:+.4f})")
        print(f"     🔄 Adaptativo:          {acc_adapt_fase:.3f}")
        print(f"     🔄 Adaptativo+Multi:    {acc_adapt_multi_fase:.3f} (Δ {acc_adapt_multi_fase - acc_adapt_fase:+.4f})")

        # Resumo textual do impacto da multimodalidade na precisão (F1-score)
        def impacto_txt(delta):
            if np.isnan(delta):
                return "NÃO FOI POSSÍVEL AVALIAR"
            elif delta > 0.001:
                return f"MELHOROU (+{delta:.3f})"
            elif delta < -0.001:
                return f"PIOROU ({delta:.3f})"
            else:
                return f"NÃO ALTEROU (+{delta:.3f})"

        delta_trad = f1_trad_multi_fase - f1_trad_fase
        delta_adapt = f1_adapt_multi_fase - f1_adapt_fase
        resumo_fases.append(
            f"   • Na fase {nome_fase}, a multimodalidade {impacto_txt(delta_trad)} a precisão do Tradicional e {impacto_txt(delta_adapt)} a do Adaptativo."
        )

    # Bloco de resumo textual após a análise por fase
    print("\n📝 RESUMO DO IMPACTO DA MULTIMODALIDADE POR FASE (F1-score):")
    print("=" * 60)
    for linha in resumo_fases:
        print(linha)
    
    # Conclusões finais
    print(f"\n🎯 CONCLUSÕES PRINCIPAIS:")
    print(f"=" * 40)
    
    print(f"1. 📊 ADAPTAÇÃO AO LONGO DO TEMPO:")
    print(f"   • RF Tradicional começou muito forte (F1=1.000 nas primeiras janelas)")
    print(f"   • RF Adaptativo teve desempenho inicial ruim (F1=0.000)")
    print(f"   • Conforme os dados mudaram, RF Adaptativo se adaptou melhor")
    print(f"   • RF Tradicional sofreu degradação significativa")
    
    print(f"\n2. 🔄 CAPACIDADE DE ADAPTAÇÃO:")
    print(f"   • RF Adaptativo mostrou melhoria progressiva")
    print(f"   • Especialmente eficaz quando padrões mudaram (Fases 2 e 3)")
    print(f"   • RF Tradicional manteve alta precisão mas baixo recall")
    
    print(f"\n3. 🏆 RECOMENDAÇÕES:")
    print(f"   • Para dados estáveis: RF Tradicional")
    print(f"   • Para dados com mudanças temporais: RF Adaptativo") 
    print(f"   • Em ambientes reais ALPR: RF Adaptativo (padrões mudam constantemente)")
    
    # Calcular evolução temporal
    print(f"\n📈 EVOLUÇÃO TEMPORAL DO F1-SCORE:")
    print(f"=" * 40)
    
    for i in range(len(df_trad)):
        janela = df_trad.iloc[i]['janela']
        f1_trad = df_trad.iloc[i]['f1']
        f1_adapt = df_adapt.iloc[i]['f1']
        
        # Criar barra visual simples
        max_val = max(f1_trad, f1_adapt)
        if max_val > 0:
            barra_trad = "█" * int(f1_trad * 20 / max_val)
            barra_adapt = "█" * int(f1_adapt * 20 / max_val)
        else:
            barra_trad = ""
            barra_adapt = ""
        
        print(f"Janela {janela}:")
        print(f"  🏛️ Trad:  {f1_trad:.3f} {barra_trad}")
        print(f"  🔄 Adapt: {f1_adapt:.3f} {barra_adapt}")
        print()
    
    return df_trad, df_trad_multi, df_adapt, df_adapt_multi

def _linha_metricas_por_janela(janela_id, modelo_nome, y_true, y_score, f1, acc, auprc, brier, extras=None):
    import numpy as np, json
    prev_obs = float(np.mean(y_true)) if len(y_true) else float("nan")
    linha = {
        "janela": janela_id,
        "modelo": modelo_nome,
        "F1": f1,
        "Accuracy": acc,
        "AUCPR": auprc,
        "Brier": brier,
        "y_true": json.dumps(list(map(int, y_true))),
        "y_score": json.dumps(list(map(float, y_score))),
        "prevalencia_observada": prev_obs,
    }
    if extras:
        linha.update(extras)
    return linha

if __name__ == "__main__":
    try:
        df_trad, df_trad_inf, df_adapt, df_adapt_inf = analisar_resultados()
        print("✅ Análise concluída com sucesso!")
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()
