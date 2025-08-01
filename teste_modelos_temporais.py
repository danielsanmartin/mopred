"""
Teste de Modelos com Mudanças Temporais
=======================================

Script principal para comparar Random Forest tradicional vs. adaptativo.
"""

from simulador_streaming_alpr import SimuladorStreamingALPR
from comparador_modelos import ComparadorModelos
import pandas as pd
import numpy as np
from haversine import haversine

def simular_mudancas_temporais(simulador):
    """Simula mudanças nos padrões de clonagem ao longo do tempo."""
    print("🔄 Simulando mudanças temporais nos dados...")
    
    if not simulador.eventos_gerados:
        print("❌ Nenhum evento gerado para simular mudanças")
        return []
    
    # Dividir eventos em fases com características diferentes
    todos_eventos = simulador.eventos_gerados.copy()
    
    # Fase 1: Comportamento normal (primeiros 33%)
    fase1_size = len(todos_eventos) // 3
    fase1_eventos = todos_eventos[:fase1_size]
    
    # Fase 2: Aumento de atividade clonada (33%-66%)
    fase2_eventos = todos_eventos[fase1_size:2*fase1_size]
    # Artificialmente aumentar eventos clonados
    contador = 0
    for evento in fase2_eventos:
        contador += 1
        if contador % 5 == 0:  # A cada 5 eventos
            evento.is_clonado = True
    
    # Fase 3: Novos padrões de clonagem (últimos 33%)
    fase3_eventos = todos_eventos[2*fase1_size:]
    # Simular novos padrões geográficos
    contador = 0
    for evento in fase3_eventos:
        contador += 1
        if contador % 3 == 0:  # A cada 3 eventos
            evento.is_clonado = True
    
    print(f"✅ Fases criadas:")
    print(f"  Fase 1: {len(fase1_eventos):,} eventos (baseline)")
    print(f"  Fase 2: {len(fase2_eventos):,} eventos (+ clonagem)")
    print(f"  Fase 3: {len(fase3_eventos):,} eventos (novos padrões)")
    
    return [fase1_eventos, fase2_eventos, fase3_eventos]

def preparar_dados_treino_inicial(fase1_eventos):
    """Prepara dados de treino inicial a partir da primeira fase."""
    print(f"\n🌱 PREPARANDO TREINO INICIAL...")
    
    if not fase1_eventos:
        return np.array([]), np.array([])
    
    # Converter eventos para DataFrame
    eventos_dict = [evento.to_dict() for evento in fase1_eventos]
    df_treino = pd.DataFrame(eventos_dict)
    
    if len(df_treino) == 0:
        return np.array([]), np.array([])
    
    # Gerar features de treino (sem e com infrações)
    features = []
    features_infracoes = []
    labels = []
    
    placas_unicas = df_treino['placa'].unique()
    
    for placa in placas_unicas:
        eventos_placa = df_treino[df_treino['placa'] == placa].sort_values('timestamp')
        
        if len(eventos_placa) < 2:
            continue
        
        # Gerar pares consecutivos para treino
        for i in range(len(eventos_placa) - 1):
            evento1 = eventos_placa.iloc[i]
            evento2 = eventos_placa.iloc[i + 1]
            
            # Pular se for a mesma câmera
            if evento1['cam'] == evento2['cam']:
                continue
            
            # Calcular features
            dist_km = haversine(
                (evento1['lat'], evento1['lon']),
                (evento2['lat'], evento2['lon'])
            )
            
            delta_t_ms = abs(evento2['timestamp'] - evento1['timestamp'])
            delta_t_segundos = delta_t_ms / 1000
            
            # Pular pares com tempo muito pequeno
            if delta_t_segundos < 30:
                continue
            
            velocidade_kmh = (dist_km / (delta_t_segundos / 3600)) if delta_t_segundos > 0 else 9999
            
            # Features para o modelo
            feature_vector = [dist_km, delta_t_segundos, velocidade_kmh]
            features.append(feature_vector)
            # Features com infrações
            num_infracoes = evento1.get('num_infracoes', 0)
            feature_vector_infracoes = [dist_km, delta_t_segundos, velocidade_kmh, num_infracoes]
            features_infracoes.append(feature_vector_infracoes)
            
            # Label baseado na velocidade e informação de clonagem (conservador para treino)
            is_suspeito = velocidade_kmh > 200 or evento1.get('is_clonado', False)
            labels.append(1 if is_suspeito else 0)
    
    X_treino = np.array(features)
    X_treino_infracoes = np.array(features_infracoes)
    y_treino = np.array(labels)
    
    print(f"✅ Dados de treino preparados:")
    print(f"   📊 {len(X_treino):,} pares de eventos")
    print(f"   ⚠️ {sum(y_treino):,} casos suspeitos ({sum(y_treino)/len(y_treino)*100:.1f}%)")
    
    return X_treino, y_treino, X_treino_infracoes

def main():
    """Função principal do teste."""
    print("🚀 INICIANDO TESTE DE MODELOS TEMPORAIS")
    print("=" * 60)
    
    try:
        # 1. Inicializar simulador
        simulador = SimuladorStreamingALPR("config.json")
        eventos = simulador.executar_simulacao_completa()
        
        if not eventos:
            print("❌ Nenhum evento gerado pelo simulador")
            return
        
        # 2. Simular mudanças temporais
        fases = simular_mudancas_temporais(simulador)
        
        if not fases:
            print("❌ Erro ao criar fases temporais")
            return
        
        # 3. Preparar dados de treino inicial (fase 1)
        X_treino, y_treino, X_treino_infracoes = preparar_dados_treino_inicial(fases[0])
        
        if len(X_treino) == 0:
            print("❌ Nenhum dado de treino gerado")
            return
        
        # 4. Inicializar comparador
        comparador = ComparadorModelos(simulador)
        
        # 5. Treinar modelo tradicional apenas uma vez (sem infrações)
        comparador.treinar_modelo_tradicional(X_treino, y_treino, usar_infracoes=False)
        # 5b. Treinar modelo tradicional com infrações
        print("\n🌟 Treinando modelo tradicional (com infrações)...")
        comparador.treinar_modelo_tradicional(X_treino_infracoes, y_treino, usar_infracoes=True)
        
        # 6. Testar em janelas temporais
        print(f"\n🕒 TESTANDO EM JANELAS TEMPORAIS...")
        
        janela_contador = 1
        
        for i, fase_eventos in enumerate(fases, 1):
            print(f"\n{'='*20} FASE {i} {'='*20}")
            
            if not fase_eventos:
                print(f"⚠️ Fase {i} vazia, pulando...")
                continue
            
            # Dividir fase em sub-janelas para análise mais granular
            tamanho_subjanela = max(1, len(fase_eventos) // 3)
            
            for j in range(3):
                inicio_janela = j * tamanho_subjanela
                fim_janela = (j + 1) * tamanho_subjanela if j < 2 else len(fase_eventos)
                
                if inicio_janela >= len(fase_eventos):
                    break
                
                janela_eventos = fase_eventos[inicio_janela:fim_janela]
                
                if len(janela_eventos) < 10:  # Mínimo de eventos para análise
                    print(f"⚠️ Janela {janela_contador} muito pequena ({len(janela_eventos)} eventos), pulando...")
                    janela_contador += 1
                    continue
                
                # Processar janela para modelo adaptativo (treino incremental)
                # Somente a partir da segunda janela (primeira é baseline)
                if janela_contador > 1:
                    comparador.processar_janela_adaptativo(janela_eventos)
                    # Novo: processar janela para modelo adaptativo com infrações
                    comparador.processar_janela_adaptativo(janela_eventos, usar_infracoes=True)
                
                # Avaliar ambos os modelos
                trad_metricas, adapt_metricas = comparador.avaliar_janela(janela_eventos, janela_contador, usar_infracoes=False)
                # Avaliar modelo tradicional com infrações
                trad_metricas_infracoes, adapt_metricas_infracoes = comparador.avaliar_janela(janela_eventos, janela_contador, usar_infracoes=True)
                
                if trad_metricas is None or adapt_metricas is None:
                    print(f"⚠️ Falha na avaliação da janela {janela_contador}")
                
                janela_contador += 1
        
        # 7. Gerar relatório final
        comparador.gerar_relatorio_final()

        # 7b. Explicabilidade XAI usando SHAP para o modelo tradicional
        try:
            import shap
        except ImportError:
            print("Instalando pacote SHAP...")
            import subprocess; subprocess.check_call(["pip", "install", "shap"])
            import shap

        print("\n🔎 EXPLICABILIDADE (XAI) PARA RANDOM FOREST TRADICIONAL:")
        modelo_rf = getattr(comparador, "modelo_tradicional", None)
        if modelo_rf is not None:
            # Detectar número de features do modelo
            n_features = getattr(modelo_rf, "n_features_in_", None)
            if n_features is None:
                n_features = modelo_rf.n_features_ if hasattr(modelo_rf, "n_features_") else 3
            # Ajustar nomes das features
            if n_features == 3:
                feature_names = ["dist_km", "delta_t_segundos", "velocidade_kmh"]
            elif n_features == 4:
                feature_names = ["dist_km", "delta_t_segundos", "velocidade_kmh", "num_infracoes"]
            else:
                feature_names = [f"feature_{i+1}" for i in range(n_features)]

            # Usar a última janela de eventos para explicação
            if len(fases) > 0 and len(fases[-1]) > 0:
                eventos_dict = [evento.to_dict() for evento in fases[-1]]
                df_teste = pd.DataFrame(eventos_dict)
                # Gerar features como no treino
                features = []
                placas_unicas = df_teste['placa'].unique()
                for placa in placas_unicas:
                    eventos_placa = df_teste[df_teste['placa'] == placa].sort_values('timestamp')
                    if len(eventos_placa) < 2:
                        continue
                    for i in range(len(eventos_placa) - 1):
                        evento1 = eventos_placa.iloc[i]
                        evento2 = eventos_placa.iloc[i + 1]
                        if evento1['cam'] == evento2['cam']:
                            continue
                        dist_km = haversine((evento1['lat'], evento1['lon']), (evento2['lat'], evento2['lon']))
                        delta_t_ms = abs(evento2['timestamp'] - evento1['timestamp'])
                        delta_t_segundos = delta_t_ms / 1000
                        if delta_t_segundos < 30:
                            continue
                        velocidade_kmh = (dist_km / (delta_t_segundos / 3600)) if delta_t_segundos > 0 else 9999
                        if n_features == 3:
                            feature_vector = [dist_km, delta_t_segundos, velocidade_kmh]
                        elif n_features == 4:
                            num_infracoes = evento1.get('num_infracoes', 0)
                            feature_vector = [dist_km, delta_t_segundos, velocidade_kmh, num_infracoes]
                        else:
                            feature_vector = [dist_km, delta_t_segundos, velocidade_kmh] + [0]*(n_features-3)
                        features.append(feature_vector)
                X_teste = np.array(features)
                if len(X_teste) > 0:
                    explainer = shap.TreeExplainer(modelo_rf)
                    shap_values = explainer.shap_values(X_teste)
                    print("\nImportância global das features:")
                    for i, nome in enumerate(feature_names):
                        print(f"  {nome}: {modelo_rf.feature_importances_[i]:.3f}")
                    print("\nExemplo de explicação SHAP para os primeiros casos (relatório amigável):")
                    preds = modelo_rf.predict(X_teste)
                    # Tradução das features
                    traducao = {
                        "dist_km": "Distância entre câmeras (km)",
                        "delta_t_segundos": "Tempo entre leituras (segundos)",
                        "velocidade_kmh": "Velocidade estimada (km/h)",
                        "num_infracoes": "Número de infrações"
                    }
                    clonados_exibidos = 0
                    for idx in range(len(X_teste)):
                        if preds[idx] != 1:
                            continue
                        clonados_exibidos += 1
                        if clonados_exibidos > 5:
                            break
                        print(f"\nCaso {idx+1} - Predição: CLONADO")
                        # Seleciona os valores SHAP corretos
                        shap_vals = shap_values[1][idx] if isinstance(shap_values, list) else shap_values[idx]
                        feat_vals = X_teste[idx]
                        print("| Característica           | Valor        | Impacto SHAP | Interpretação           |")
                        print("|--------------------------|--------------|--------------|-------------------------|")
                        resumo = []
                        for i, nome in enumerate(feature_names):
                            nome_pt = traducao.get(nome, nome)
                            valor = feat_vals[i]
                            # Se shap_vals[i] for array, pega o valor da classe positiva (índice 1), senão usa direto
                            impacto_raw = shap_vals[i]
                            if isinstance(impacto_raw, (np.ndarray, list)):
                                if len(impacto_raw) > 1:
                                    impacto_val = impacto_raw[1]
                                else:
                                    impacto_val = impacto_raw[0]
                            else:
                                impacto_val = impacto_raw
                            if abs(impacto_val) > 0.05:
                                emoji = "🔴"
                                interpret = "Alto impacto"
                                resumo.append(f"{nome_pt} teve forte influência na decisão.")
                            elif abs(impacto_val) > 0.01:
                                emoji = "🟡"
                                interpret = "Impacto moderado"
                            else:
                                emoji = "🟢"
                                interpret = "Baixo impacto"
                            print(f"| {nome_pt:24} | {valor:10.3f} | {impacto_val:10.3f} | {emoji} {interpret:18} |")
                        if resumo:
                            print("Resumo: " + " ".join(resumo))
                        else:
                            print("Resumo: Nenhuma característica teve impacto relevante para indicar clonagem.")
                else:
                    print("Sem dados suficientes para explicação XAI na última fase.")
            else:
                print("Sem dados de teste para explicação XAI.")
        else:
            print("Modelo tradicional não encontrado para XAI.")

        # 8. Teste adicional com janelas do simulador streaming
        print(f"\n🪟 TESTE ADICIONAL COM STREAMING POR JANELAS...")
        testar_streaming_janelas(simulador, comparador)
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

def testar_streaming_janelas(simulador, comparador):
    """Teste adicional usando o modo de janelas temporais do simulador."""
    try:
        print("🔄 Reinicializando modelo adaptativo para teste limpo...")
        
        # Reinicializar modelo adaptativo para teste limpo
        from comparador_modelos import AdaptiveRandomForestWrapper
        comparador.modelo_adaptativo = AdaptiveRandomForestWrapper(
            n_models=10,
            seed=42
        )
        
        # Usar streaming por janelas (2 horas por janela para ter dados suficientes)
        janelas_stream = simulador.streaming_janelas_temporais(tamanho_janela_horas=2.0)
        
        janelas_processadas = 0
        janela_anterior = None
        
        for i, janela_eventos in enumerate(janelas_stream):
            if janelas_processadas >= 5:  # Testar apenas primeiras 5 janelas
                break
            
            print(f"\n--- Janela Streaming {i+1} ---")
            
            # Treinar modelo adaptativo com janela anterior
            if janela_anterior is not None and len(janela_anterior) > 10:
                print(f"🔄 Treinando modelo adaptativo com janela anterior...")
                comparador.processar_janela_adaptativo(janela_anterior)
            
            # Avaliar na janela atual
            if len(janela_eventos) > 10:
                janela_numero = f"Stream-{i+1}"
                trad_metricas, adapt_metricas = comparador.avaliar_janela(janela_eventos, janela_numero)
                
                if trad_metricas is not None and adapt_metricas is not None:
                    janelas_processadas += 1
            else:
                print(f"⚠️ Janela {i+1} muito pequena para análise")
            
            janela_anterior = janela_eventos
        
        print(f"✅ Teste de streaming concluído com {janelas_processadas} janelas processadas")

        # Explicabilidade SHAP para casos clonados do streaming
        modelo_rf = getattr(comparador, "modelo_tradicional", None)
        if modelo_rf is not None:
            try:
                import shap
            except ImportError:
                print("Instalando pacote SHAP...")
                import subprocess; subprocess.check_call(["pip", "install", "shap"])
                import shap

            print("\n🔎 EXPLICABILIDADE (XAI) PARA CASOS CLONADOS DO STREAMING:")
            # Coletar todos eventos das janelas do streaming
            eventos_streaming = []
            janelas_stream = simulador.streaming_janelas_temporais(tamanho_janela_horas=2.0)
            for janela_eventos in janelas_stream:
                eventos_streaming.extend(janela_eventos)
            if len(eventos_streaming) == 0:
                print("Sem eventos de streaming para explicação XAI.")
                return
            eventos_dict = [evento.to_dict() for evento in eventos_streaming]
            df_teste = pd.DataFrame(eventos_dict)
            # Gerar features como no treino
            n_features = getattr(modelo_rf, "n_features_in_", None)
            if n_features is None:
                n_features = modelo_rf.n_features_ if hasattr(modelo_rf, "n_features_") else 3
            if n_features == 3:
                feature_names = ["dist_km", "delta_t_segundos", "velocidade_kmh"]
            elif n_features == 4:
                feature_names = ["dist_km", "delta_t_segundos", "velocidade_kmh", "num_infracoes"]
            else:
                feature_names = [f"feature_{i+1}" for i in range(n_features)]
            features = []
            placas_unicas = df_teste['placa'].unique()
            for placa in placas_unicas:
                eventos_placa = df_teste[df_teste['placa'] == placa].sort_values('timestamp')
                if len(eventos_placa) < 2:
                    continue
                for i in range(len(eventos_placa) - 1):
                    evento1 = eventos_placa.iloc[i]
                    evento2 = eventos_placa.iloc[i + 1]
                    if evento1['cam'] == evento2['cam']:
                        continue
                    dist_km = haversine((evento1['lat'], evento1['lon']), (evento2['lat'], evento2['lon']))
                    delta_t_ms = abs(evento2['timestamp'] - evento1['timestamp'])
                    delta_t_segundos = delta_t_ms / 1000
                    if delta_t_segundos < 30:
                        continue
                    velocidade_kmh = (dist_km / (delta_t_segundos / 3600)) if delta_t_segundos > 0 else 9999
                    if n_features == 3:
                        feature_vector = [dist_km, delta_t_segundos, velocidade_kmh]
                    elif n_features == 4:
                        num_infracoes = evento1.get('num_infracoes', 0)
                        feature_vector = [dist_km, delta_t_segundos, velocidade_kmh, num_infracoes]
                    else:
                        feature_vector = [dist_km, delta_t_segundos, velocidade_kmh] + [0]*(n_features-3)
                    features.append(feature_vector)
            X_teste = np.array(features)
            if len(X_teste) > 0:
                explainer = shap.TreeExplainer(modelo_rf)
                shap_values = explainer.shap_values(X_teste)
                print("\nImportância global das features:")
                for i, nome in enumerate(feature_names):
                    print(f"  {nome}: {modelo_rf.feature_importances_[i]:.3f}")
                print("\nExemplo de explicação SHAP para os primeiros casos clonados do streaming:")
                preds = modelo_rf.predict(X_teste)
                traducao = {
                    "dist_km": "Distância entre câmeras (km)",
                    "delta_t_segundos": "Tempo entre leituras (segundos)",
                    "velocidade_kmh": "Velocidade estimada (km/h)",
                    "num_infracoes": "Número de infrações"
                }
                clonados_exibidos = 0
                for idx in range(len(X_teste)):
                    if preds[idx] != 1:
                        continue
                    clonados_exibidos += 1
                    if clonados_exibidos > 5:
                        break
                    print(f"\nCaso {idx+1} - Predição: CLONADO")
                    shap_vals = shap_values[1][idx] if isinstance(shap_values, list) else shap_values[idx]
                    feat_vals = X_teste[idx]
                    print("| Característica           | Valor        | Impacto SHAP | Interpretação           |")
                    print("|--------------------------|--------------|--------------|-------------------------|")
                    resumo = []
                    for i, nome in enumerate(feature_names):
                        nome_pt = traducao.get(nome, nome)
                        valor = feat_vals[i]
                        impacto_raw = shap_vals[i]
                        if isinstance(impacto_raw, (np.ndarray, list)):
                            if len(impacto_raw) > 1:
                                impacto_val = impacto_raw[1]
                            else:
                                impacto_val = impacto_raw[0]
                        else:
                            impacto_val = impacto_raw
                        if abs(impacto_val) > 0.05:
                            emoji = "🔴"
                            interpret = "Alto impacto"
                            resumo.append(f"{nome_pt} teve forte influência na decisão.")
                        elif abs(impacto_val) > 0.01:
                            emoji = "🟡"
                            interpret = "Impacto moderado"
                        else:
                            emoji = "🟢"
                            interpret = "Baixo impacto"
                        print(f"| {nome_pt:24} | {valor:10.3f} | {impacto_val:10.3f} | {emoji} {interpret:18} |")
                    if resumo:
                        print("Resumo: " + " ".join(resumo))
                    else:
                        print("Resumo: Nenhuma característica teve impacto relevante para indicar clonagem.")
            else:
                print("Sem dados suficientes para explicação XAI no streaming.")
        
    except Exception as e:
        print(f"❌ Erro no teste de streaming: {e}")

if __name__ == "__main__":
    main()
