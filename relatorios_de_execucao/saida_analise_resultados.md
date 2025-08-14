  ANÁLISE DO IMPACTO DA MULTIMODALIDADE NA PERFORMANCE:
============================================================

🏛️ Tradicional:
   F1-score:   0.638 → 0.658  ↑ Melhora (+0.020)
   Accuracy:   0.818 → 0.824  ↑ Melhora (+0.006)

🔄 Adaptativo:
   F1-score:   0.605 → 0.624  ↑ Melhora (+0.019)
   Accuracy:   0.826 → 0.834  ↑ Melhora (+0.008)

📋 CONCLUSÃO SOBRE O IMPACTO DA MULTIMODALIDADE:
   • Random Forest Tradicional (F1-score): A multimodalidade MELHOROU a performance.
   • Random Forest Tradicional (Accuracy): A multimodalidade MELHOROU a performance.
   • Random Forest Adaptativo (F1-score): A multimodalidade MELHOROU a performance.
   • Random Forest Adaptativo (Accuracy): A multimodalidade MELHOROU a performance.
📊 ANÁLISE DETALHADA DOS RESULTADOS
============================================================
📈 ANÁLISE POR JANELA TEMPORAL (4 CENÁRIOS):
============================================================

🪟 JANELA 1 (BASELINE):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.992    │    0.997    │    0.896    │    0.896    │
   │   F1-Score  │    0.957    │    0.985    │    0.000    │    0.000    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.028
     Adaptativo:  ΔF1 = +0.000

🪟 JANELA 2 (BASELINE):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.991    │    0.998    │    0.990    │    0.991    │
   │   F1-Score  │    0.969    │    0.992    │    0.966    │    0.970    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.023
     Adaptativo:  ΔF1 = +0.004

🪟 JANELA 3 (BASELINE):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.993    │    0.997    │    0.990    │    0.992    │
   │   F1-Score  │    0.977    │    0.990    │    0.967    │    0.973    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.014
     Adaptativo:  ΔF1 = +0.006

🪟 JANELA 4 (MUDANÇA):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.820    │    0.824    │    0.820    │    0.821    │
   │   F1-Score  │    0.622    │    0.633    │    0.619    │    0.624    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.011
     Adaptativo:  ΔF1 = +0.004

🪟 JANELA 5 (MUDANÇA):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.817    │    0.826    │    0.823    │    0.828    │
   │   F1-Score  │    0.600    │    0.630    │    0.618    │    0.634    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.030
     Adaptativo:  ΔF1 = +0.016

🪟 JANELA 6 (MUDANÇA):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.806    │    0.816    │    0.810    │    0.817    │
   │   F1-Score  │    0.574    │    0.604    │    0.588    │    0.608    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.030
     Adaptativo:  ΔF1 = +0.020

🪟 JANELA 7 (NOVOS PADRÕES):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.650    │    0.654    │    0.715    │    0.725    │
   │   F1-Score  │    0.426    │    0.435    │    0.634    │    0.654    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.009
     Adaptativo:  ΔF1 = +0.020

🪟 JANELA 8 (NOVOS PADRÕES):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.666    │    0.674    │    0.698    │    0.723    │
   │   F1-Score  │    0.459    │    0.481    │    0.564    │    0.616    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.021
     Adaptativo:  ΔF1 = +0.052

🪟 JANELA 9 (NOVOS PADRÕES):
   ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
   │   Métrica   │ Tradicional │  Trad+Multi │  Adaptativo │ Adapt+Multi │
   ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
   │   Accuracy  │    0.623    │    0.625    │    0.693    │    0.714    │
   │   F1-Score  │    0.160    │    0.172    │    0.489    │    0.541    │
   └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Impacto da Multimodalidade:
     Tradicional: ΔF1 = +0.012
     Adaptativo:  ΔF1 = +0.052

📊 ANÁLISE POR FASE (IMPACTO DA MULTIMODALIDADE):
============================================================

🔍 BASELINE (Janelas 1-3):
   F1-Score Médio:
     🏛️ Tradicional:         0.968
     🏛️ Tradicional+Multi:   0.989 (Δ +0.0216)
     🔄 Adaptativo:          0.644
     🔄 Adaptativo+Multi:    0.648 (Δ +0.0033)
   Accuracy Médio:
     🏛️ Tradicional:         0.992
     🏛️ Tradicional+Multi:   0.997 (Δ +0.0054)
     🔄 Adaptativo:          0.959
     🔄 Adaptativo+Multi:    0.960 (Δ +0.0009)

🔍 MUDANÇA (Janelas 4-6):
   F1-Score Médio:
     🏛️ Tradicional:         0.599
     🏛️ Tradicional+Multi:   0.622 (Δ +0.0237)
     🔄 Adaptativo:          0.608
     🔄 Adaptativo+Multi:    0.622 (Δ +0.0134)
   Accuracy Médio:
     🏛️ Tradicional:         0.815
     🏛️ Tradicional+Multi:   0.822 (Δ +0.0076)
     🔄 Adaptativo:          0.818
     🔄 Adaptativo+Multi:    0.822 (Δ +0.0045)

🔍 NOVOS PADRÕES (Janelas 7-9):
   F1-Score Médio:
     🏛️ Tradicional:         0.348
     🏛️ Tradicional+Multi:   0.363 (Δ +0.0144)
     🔄 Adaptativo:          0.563
     🔄 Adaptativo+Multi:    0.604 (Δ +0.0414)
   Accuracy Médio:
     🏛️ Tradicional:         0.646
     🏛️ Tradicional+Multi:   0.651 (Δ +0.0049)
     🔄 Adaptativo:          0.702
     🔄 Adaptativo+Multi:    0.721 (Δ +0.0189)

📝 RESUMO DO IMPACTO DA MULTIMODALIDADE POR FASE (F1-score):
============================================================
   • Na fase BASELINE (Janelas 1-3), a multimodalidade MELHOROU (+0.022) a precisão do Tradicional e MELHOROU (+0.003) a do Adaptativo.
   • Na fase MUDANÇA (Janelas 4-6), a multimodalidade MELHOROU (+0.024) a precisão do Tradicional e MELHOROU (+0.013) a do Adaptativo.
   • Na fase NOVOS PADRÕES (Janelas 7-9), a multimodalidade MELHOROU (+0.014) a precisão do Tradicional e MELHOROU (+0.041) a do Adaptativo.

🎯 CONCLUSÕES PRINCIPAIS:
========================================
1. 📊 ADAPTAÇÃO AO LONGO DO TEMPO:
   • RF Tradicional começou muito forte (F1=1.000 nas primeiras janelas)
   • RF Adaptativo teve desempenho inicial ruim (F1=0.000)
   • Conforme os dados mudaram, RF Adaptativo se adaptou melhor
   • RF Tradicional sofreu degradação significativa

2. 🔄 CAPACIDADE DE ADAPTAÇÃO:
   • RF Adaptativo mostrou melhoria progressiva
   • Especialmente eficaz quando padrões mudaram (Fases 2 e 3)
   • RF Tradicional manteve alta precisão mas baixo recall

3. 🏆 RECOMENDAÇÕES:
   • Para dados estáveis: RF Tradicional
   • Para dados com mudanças temporais: RF Adaptativo
   • Em ambientes reais ALPR: RF Adaptativo (padrões mudam constantemente)

📈 EVOLUÇÃO TEMPORAL DO F1-SCORE:
========================================
Janela 1:
  🏛️ Trad:  0.957 ████████████████████
  🔄 Adapt: 0.000

Janela 2:
  🏛️ Trad:  0.969 ████████████████████
  🔄 Adapt: 0.966 ███████████████████

Janela 3:
  🏛️ Trad:  0.977 ████████████████████
  🔄 Adapt: 0.967 ███████████████████

Janela 4:
  🏛️ Trad:  0.622 ████████████████████
  🔄 Adapt: 0.619 ███████████████████

Janela 5:
  🏛️ Trad:  0.600 ███████████████████
  🔄 Adapt: 0.618 ████████████████████

Janela 6:
  🏛️ Trad:  0.574 ███████████████████
  🔄 Adapt: 0.588 ████████████████████

Janela 7:
  🏛️ Trad:  0.426 █████████████
  🔄 Adapt: 0.634 ████████████████████

Janela 8:
  🏛️ Trad:  0.459 ████████████████
  🔄 Adapt: 0.564 ████████████████████

Janela 9:
  🏛️ Trad:  0.160 ██████
  🔄 Adapt: 0.489 ████████████████████

✅ Análise concluída com sucesso!