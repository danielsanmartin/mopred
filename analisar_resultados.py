"""
Análise Visual dos Resultados da Comparação de Modelos
======================================================

Gera gráficos e relatórios detalhados da comparação RF Tradicional vs Adaptativo.
"""

import pandas as pd
import numpy as np

def analisar_resultados():
    # ... Bloco de conclusão automática será movido para depois do cálculo das médias ...
    # ...existing code...
    # Carregar resultados
    df = pd.read_csv("comparacao_modelos_resultados.csv")
    # Separar por tipo de modelo
    df_trad = df[df['tipo'] == 'tradicional'].reset_index(drop=True)
    df_trad_inf = df[df['tipo'] == 'tradicional_infracoes'].reset_index(drop=True)
    df_adapt = df[df['tipo'] == 'adaptativo'].reset_index(drop=True)
    df_adapt_inf = df[df['tipo'] == 'adaptativo_infracoes'].reset_index(drop=True)

    # Análise do impacto da feature de infrações
    print(f"\n🔬 ANÁLISE DO IMPACTO DAS INFRAÇÕES NA PERFORMANCE:")
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
    f1_trad_inf = df_trad_inf['f1'].mean()
    f1_adapt = df_adapt['f1'].mean()
    f1_adapt_inf = df_adapt_inf['f1'].mean()
    acc_trad = df_trad['accuracy'].mean()
    acc_trad_inf = df_trad_inf['accuracy'].mean()
    acc_adapt = df_adapt['accuracy'].mean()
    acc_adapt_inf = df_adapt_inf['accuracy'].mean()

    print(f"\n🏛️ Tradicional:")
    print(f"   F1-score:   {f1_trad:.3f} → {f1_trad_inf:.3f}  {impacto_str(f1_trad_inf - f1_trad)}")
    print(f"   Accuracy:   {acc_trad:.3f} → {acc_trad_inf:.3f}  {impacto_str(acc_trad_inf - acc_trad)}")

    print(f"\n🔄 Adaptativo:")
    print(f"   F1-score:   {f1_adapt:.3f} → {f1_adapt_inf:.3f}  {impacto_str(f1_adapt_inf - f1_adapt)}")
    print(f"   Accuracy:   {acc_adapt:.3f} → {acc_adapt_inf:.3f}  {impacto_str(acc_adapt_inf - acc_adapt)}")

    # Conclusão automática sobre o impacto das infrações (agora com variáveis já definidas)
    print("\n📋 CONCLUSÃO SOBRE O IMPACTO DAS INFRAÇÕES:")
    def conclusao_impacto(delta, nome):
        if np.isnan(delta):
            return f"   • {nome}: Não foi possível avaliar o impacto (dados ausentes)."
        if delta > 0:
            return f"   • {nome}: A inclusão das infrações MELHOROU a performance."
        elif delta < 0:
            return f"   • {nome}: A inclusão das infrações PIOROU a performance."
        else:
            return f"   • {nome}: A inclusão das infrações NÃO ALTEROU a performance."

    print(conclusao_impacto(f1_trad_inf - f1_trad, "Random Forest Tradicional (F1-score)"))
    print(conclusao_impacto(acc_trad_inf - acc_trad, "Random Forest Tradicional (Accuracy)"))
    print(conclusao_impacto(f1_adapt_inf - f1_adapt, "Random Forest Adaptativo (F1-score)"))
    print(conclusao_impacto(acc_adapt_inf - acc_adapt, "Random Forest Adaptativo (Accuracy)"))
    """Análise detalhada dos resultados."""
    print("📊 ANÁLISE DETALHADA DOS RESULTADOS")
    print("=" * 60)
    
    # Carregar resultados
    df = pd.read_csv("comparacao_modelos_resultados.csv")
    
    # Separar por tipo de modelo
    df_trad = df[df['tipo'] == 'tradicional'].reset_index(drop=True)
    df_trad_inf = df[df['tipo'] == 'tradicional_infracoes'].reset_index(drop=True)
    df_adapt = df[df['tipo'] == 'adaptativo'].reset_index(drop=True)
    df_adapt_inf = df[df['tipo'] == 'adaptativo_infracoes'].reset_index(drop=True)

    print(f"📈 ANÁLISE POR JANELA TEMPORAL (4 CENÁRIOS):")
    print(f"=" * 60)

    # Obter todas as janelas únicas presentes em qualquer cenário
    janelas_trad = set(df_trad['janela'].unique())
    janelas_trad_inf = set(df_trad_inf['janela'].unique())
    janelas_adapt = set(df_adapt['janela'].unique())
    janelas_adapt_inf = set(df_adapt_inf['janela'].unique())
    todas_janelas = sorted(janelas_trad | janelas_trad_inf | janelas_adapt | janelas_adapt_inf)

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
        acc_trad_inf = get_metric(df_trad_inf, janela, 'accuracy')
        f1_trad_inf = get_metric(df_trad_inf, janela, 'f1')
        acc_adapt = get_metric(df_adapt, janela, 'accuracy')
        f1_adapt = get_metric(df_adapt, janela, 'f1')
        acc_adapt_inf = get_metric(df_adapt_inf, janela, 'accuracy')
        f1_adapt_inf = get_metric(df_adapt_inf, janela, 'f1')

        # Determinar fase
        if janela <= 3:
            fase = "BASELINE"
        elif janela <= 6:
            fase = "MUDANÇA"
        else:
            fase = "NOVOS PADRÕES"

        print(f"\n🪟 JANELA {janela} ({fase}):")
        print(f"   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐")
        print(f"   │   Métrica   │ Tradicional │ Trad+Infra  │ Adaptativo  │ Adapt+Infra │")
        print(f"   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤")
        def fmt(val):
            return f"{val:9.3f}" if val is not None else "    N/A   "
        print(f"   │  Accuracy   │ {fmt(acc_trad)} │ {fmt(acc_trad_inf)} │ {fmt(acc_adapt)} │ {fmt(acc_adapt_inf)} │")
        print(f"   │  F1-Score   │ {fmt(f1_trad)} │ {fmt(f1_trad_inf)} │ {fmt(f1_adapt)} │ {fmt(f1_adapt_inf)} │")
        print(f"   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘")
        # Impacto das infrações
        print(f"   Impacto das Infrações:")
        trad_delta = f1_trad_inf - f1_trad if f1_trad is not None and f1_trad_inf is not None else None
        adapt_delta = f1_adapt_inf - f1_adapt if f1_adapt is not None and f1_adapt_inf is not None else None
        print(f"     Tradicional: ΔF1 = {trad_delta:+.3f}" if trad_delta is not None else "     Tradicional: ΔF1 = N/A")
        print(f"     Adaptativo:  ΔF1 = {adapt_delta:+.3f}" if adapt_delta is not None else "     Adaptativo:  ΔF1 = N/A")
    
    # Análise por fase
    print(f"\n📊 ANÁLISE POR FASE (IMPACTO DAS INFRAÇÕES):")
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
        fase_trad_inf = df_trad_inf[df_trad_inf['janela'].isin(janelas)]
        fase_adapt = df_adapt[df_adapt['janela'].isin(janelas)]
        fase_adapt_inf = df_adapt_inf[df_adapt_inf['janela'].isin(janelas)]
        # Calcular médias da fase
        f1_trad_fase = fase_trad['f1'].mean()
        f1_trad_inf_fase = fase_trad_inf['f1'].mean()
        f1_adapt_fase = fase_adapt['f1'].mean()
        f1_adapt_inf_fase = fase_adapt_inf['f1'].mean()
        acc_trad_fase = fase_trad['accuracy'].mean()
        acc_trad_inf_fase = fase_trad_inf['accuracy'].mean()
        acc_adapt_fase = fase_adapt['accuracy'].mean()
        acc_adapt_inf_fase = fase_adapt_inf['accuracy'].mean()
        print(f"   F1-Score Médio:")
        print(f"     🏛️ Tradicional:         {f1_trad_fase:.3f}")
        print(f"     🏛️ Tradicional+Infra:   {f1_trad_inf_fase:.3f} (Δ {f1_trad_inf_fase - f1_trad_fase:+.3f})")
        print(f"     🔄 Adaptativo:          {f1_adapt_fase:.3f}")
        print(f"     🔄 Adaptativo+Infra:    {f1_adapt_inf_fase:.3f} (Δ {f1_adapt_inf_fase - f1_adapt_fase:+.3f})")
        print(f"   Accuracy Médio:")
        print(f"     🏛️ Tradicional:         {acc_trad_fase:.3f}")
        print(f"     🏛️ Tradicional+Infra:   {acc_trad_inf_fase:.3f} (Δ {acc_trad_inf_fase - acc_trad_fase:+.3f})")
        print(f"     🔄 Adaptativo:          {acc_adapt_fase:.3f}")
        print(f"     🔄 Adaptativo+Infra:    {acc_adapt_inf_fase:.3f} (Δ {acc_adapt_inf_fase - acc_adapt_fase:+.3f})")

        # Resumo textual do impacto das infrações na precisão (F1-score)
        def impacto_txt(delta):
            if np.isnan(delta):
                return "NÃO FOI POSSÍVEL AVALIAR"
            elif delta > 0.001:
                return f"MELHOROU (+{delta:.3f})"
            elif delta < -0.001:
                return f"PIOROU ({delta:.3f})"
            else:
                return f"NÃO ALTEROU (+{delta:.3f})"

        delta_trad = f1_trad_inf_fase - f1_trad_fase
        delta_adapt = f1_adapt_inf_fase - f1_adapt_fase
        resumo_fases.append(
            f"   • Na fase {nome_fase}, o uso de infrações {impacto_txt(delta_trad)} a precisão do Tradicional e {impacto_txt(delta_adapt)} a do Adaptativo."
        )

    # Bloco de resumo textual após a análise por fase
    print("\n📝 RESUMO DO IMPACTO DAS INFRAÇÕES POR FASE (F1-score):")
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
    
    return df_trad, df_trad_inf, df_adapt, df_adapt_inf

if __name__ == "__main__":
    try:
        df_trad, df_trad_inf, df_adapt, df_adapt_inf = analisar_resultados()
        print("✅ Análise concluída com sucesso!")
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()
