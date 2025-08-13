"""
Teste de Modelos com Mudanças Temporais
=======================================

Script principal para comparar Random Forest tradicional vs. adaptativo.
"""

from simulador_streaming_alpr import SimuladorStreamingALPR
from comparador_modelos import ComparadorModelos
import json
import pandas as pd
import numpy as np
import hashlib
import hmac
from haversine import haversine
from joblib import Parallel, delayed
from utils import processar_placa_basico
try:
    from imblearn.over_sampling import SMOTE
except ImportError:
    SMOTE = None

def pseudonimizar_placa(placa, salt="mopred_2024_salt_key"):
    """
    Gera um pseudônimo irreversível para a placa usando SHA-256.
    
    Args:
        placa: Placa original (ex: "ABC1234")
        salt: Chave secreta para tornar o hash mais seguro
    
    Returns:
        String pseudonimizada (ex: "PSEUDO_A1B2C3D4")
    """
    # Normalizar placa (remover espaços, converter para maiúscula)
    placa_normalizada = placa.upper().replace(" ", "").replace("-", "")
    
    # Gerar hash seguro com salt
    hash_obj = hmac.new(
        salt.encode('utf-8'), 
        placa_normalizada.encode('utf-8'), 
        hashlib.sha256
    )
    hash_hex = hash_obj.hexdigest()
    
    # Usar apenas os primeiros 8 caracteres para pseudônimo mais legível
    pseudonimo = f"PSEUDO_{hash_hex[:8].upper()}"
    
    return pseudonimo

def aplicar_pseudonimizacao_eventos(eventos, config=None):
    """
    Aplica pseudonimização em todos os eventos.
    
    Args:
        eventos: Lista de eventos com placas originais
        config: Configuração com salt personalizado
    
    Returns:
        Lista de eventos com placas pseudonimizadas
    """
    print("🔒 Aplicando pseudonimização nas placas...")
    
    # Usar salt do config ou padrão
    salt = config.get("salt_pseudonimizacao", "mopred_doutorado_2024_chave_secreta") if config else "mopred_doutorado_2024_chave_secreta"
    
    placas_mapeadas = {}
    total_pseudonimizadas = 0
    
    for evento in eventos:
        placa_original = evento.placa
        
        # Verificar se já foi pseudonimizada
        if placa_original not in placas_mapeadas:
            placa_pseudo = pseudonimizar_placa(placa_original, salt)
            placas_mapeadas[placa_original] = placa_pseudo
            total_pseudonimizadas += 1
        
        # Substituir placa original pela pseudonimizada
        evento.placa = placas_mapeadas[placa_original]
    
    print(f"✅ {total_pseudonimizadas} placas únicas pseudonimizadas")
    print(f"📊 Total de eventos processados: {len(eventos)}")
    
    return eventos

def simular_mudancas_temporais(simulador, config):
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
    
    # Simular novos padrões geográficos usando coordenadas do config
    print("  📍 Criando zonas quentes baseadas na configuração...")
    
    # Selecionar algumas cidades como zonas quentes (cidades maiores ou estratégicas)
    cidades_config = config.get("lat_lon_por_cidade", {})
    zonas_quentes = config.get("zonas_quentes", [])  # Cidades estratégicas
    raio_zona = config.get("raio_zonas_quentes", 0.2)  # 0.2 equivale a aproximadamente 20km

    total_clonados_zona = 0
    for evento in fase3_eventos:
        lat, lon = evento.lat, evento.lon
        
        # Verificar se está próximo a alguma zona quente
        for cidade in zonas_quentes:
            if cidade in cidades_config:
                cidade_lat, cidade_lon = cidades_config[cidade]
                # Verificar se está dentro do raio da cidade
                if (abs(lat - cidade_lat) < raio_zona and 
                    abs(lon - cidade_lon) < raio_zona):
                    evento.is_clonado = True
                    total_clonados_zona += 1
                    break
    
    print(f"  ✅ {total_clonados_zona} eventos marcados como clonados nas zonas quentes")
    
    print(f"✅ Fases criadas:")
    print(f"  Fase 1: {len(fase1_eventos):,} eventos (baseline)")
    print(f"  Fase 2: {len(fase2_eventos):,} eventos (+ clonagem)")
    print(f"  Fase 3: {len(fase3_eventos):,} eventos (novos padrões)")
    
    return [fase1_eventos, fase2_eventos, fase3_eventos]

def preparar_dados_treino_inicial(fase1_eventos, n_jobs, config=None):
    print(f"\n🌱 PREPARANDO TREINO INICIAL...")

    if not fase1_eventos:
        return np.array([]), np.array([]), np.array([])

    eventos_dict = [evento.to_dict() for evento in fase1_eventos]
    df_treino = pd.DataFrame(eventos_dict)

    if len(df_treino) == 0:
        return np.array([]), np.array([]), np.array([])

    placas_unicas = df_treino['placa'].unique()

    # Usar a nova função de processamento básico para treino inicial
    resultados = Parallel(n_jobs=n_jobs, backend="multiprocessing")(
        delayed(processar_placa_basico)(df_treino[df_treino['placa'] == placa].sort_values('timestamp'))
        for placa in placas_unicas
    )

    features, labels = [], []
    features_multimodal = []  # Para armazenar features com 5 dimensões
    resultados_validos = 0
    total_features_ignorados = 0
    total_labels_ignorados = 0
    for r in resultados:
        if isinstance(r, (list, tuple)) and len(r) >= 3:
            f, l, f_semelhanca = r[:3]
            if len(f) == len(l) and len(f_semelhanca) == len(l):
                for feat, label, feat_mm in zip(f, l, f_semelhanca):
                    # Classificação binária:
                    # 0: não clonado
                    # 1: clonado (idêntico ou não idêntico)
                    if label == 0:
                        labels.append(0)
                    else:
                        labels.append(1)
                    features.append(feat)
                    features_multimodal.append(feat_mm)
                resultados_validos += 1
            else:
                print(f"⚠️ Inconsistência: {len(f)} features vs {len(l)} labels ignorados para uma placa.")
                total_features_ignorados += len(f)
                total_labels_ignorados += len(l)
        else:
            print(f"⚠️ Resultado inválido ignorado: {r}")
    if resultados_validos < len(resultados):
        print(f"⚠️ {len(resultados) - resultados_validos} resultados ignorados por formato inesperado.")
    if total_features_ignorados > 0 or total_labels_ignorados > 0:
        print(f"⚠️ Total ignorado por inconsistência: {total_features_ignorados} features, {total_labels_ignorados} labels.")

    X_treino = np.array(features, dtype=np.float32)
    X_treino_multimodal = np.array(features_multimodal, dtype=np.float32)  # Features com 5 dimensões
    y_treino = np.array(labels, dtype=np.int32).ravel()

    # Verificar se deve usar SMOTE
    usar_smote = config.get("usar_smote", True) if config else True
    
    if usar_smote:
        return balancear_com_smote_binario(X_treino, X_treino_multimodal, y_treino, features_multimodal, config)
    else:
        print("⚠️ SMOTE desabilitado pela configuração.")
        print(f"✅ Dados de treino preparados (sem balanceamento):")
        print(f"   📊 {len(X_treino):,} pares de eventos")
        for classe in [0, 1]:
            print(f"   Classe {classe}: {np.sum(y_treino == classe)} exemplos")
        if len(features_multimodal) > 0:
            print(f"   🧬 Média de semelhança: {np.mean([f[-1] for f in features_multimodal]):.3f}")
        else:
            print(f"   🧬 Média de semelhança: N/A")
        return X_treino, X_treino_multimodal, y_treino

def interpretar_impacto_shap_dinamico(valor_shap, todos_shap_values):
    abs_valor = abs(valor_shap)
    abs_todos = [abs(v) for v in todos_shap_values]
    
    # Usar thresholds mais baixos para capturar melhor as nuances
    p60 = np.percentile(abs_todos, 60)  # Mais baixo que P75
    p30 = np.percentile(abs_todos, 30)  # Mais baixo que P25
    
    # Determinar magnitude do impacto
    if abs_valor >= p60:
        nivel = "Alto impacto"
        emoji = "🔴"  # Vermelho
    elif abs_valor >= p30:
        nivel = "Impacto moderado"  
        emoji = "🟡"  # Amarelo
    else:
        nivel = "Baixo impacto"
        emoji = "🟢"  # Verde
    
    # Adicionar direção (+ ou -)
    if valor_shap >= 0:
        return f"{emoji} + {nivel}"  # Aumenta probabilidade
    else:
        return f"{emoji} - {nivel}"  # Diminui probabilidade

def gerar_relatorio_xai_shap(modelo_rf, eventos, titulo_relatorio, max_casos_exibidos=5):
    """
    Gera e imprime relatório de explicabilidade SHAP para casos clonados.
    
    Args:
        modelo_rf: Modelo Random Forest treinado
        eventos: Lista de eventos para análise
        titulo_relatorio: Título do relatório a ser exibido
        max_casos_exibidos: Número máximo de casos clonados a serem exibidos (padrão: 5)
    """
    try:
        import shap
    except ImportError:
        print("Instalando pacote SHAP...")
        import subprocess; subprocess.check_call(["pip", "install", "shap"])
        import shap
    
    print(f"\n{titulo_relatorio}")
    
    if not eventos:
        print("Sem eventos para explicação XAI.")
        return
    
    # Preparar dados de teste
    eventos_dict = [evento.to_dict() for evento in eventos]
    df_teste = pd.DataFrame(eventos_dict)
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
            num_infracoes = evento1.get('num_infracoes', 0)
            
            # Decompor semelhança em 3 features booleanas
            marca_modelo_igual = 1.0 if (evento1.get('marca') == evento2.get('marca') and 
                                         evento1.get('modelo') == evento2.get('modelo')) else 0.0
            tipo_igual = 1.0 if evento1.get('tipo') == evento2.get('tipo') else 0.0
            cor_igual = 1.0 if evento1.get('cor') == evento2.get('cor') else 0.0
            
            feature_vector = [dist_km, delta_t_segundos, velocidade_kmh, num_infracoes, 
                            marca_modelo_igual, tipo_igual, cor_igual]
            features.append(feature_vector)
    
    X_teste = np.array(features)
    if len(X_teste) == 0:
        print("Sem dados suficientes para explicação XAI.")
        return
    
    # Gerar explicações SHAP
    explainer = shap.TreeExplainer(modelo_rf)
    shap_values = explainer.shap_values(X_teste)
    
    # Importância global das features
    feature_names = ["dist_km", "delta_t_segundos", "velocidade_kmh", "num_infracoes", "marca_modelo_igual", "tipo_igual", "cor_igual"]
    print("Importância global das features:")
    n_features_modelo = len(modelo_rf.feature_importances_)
    for i in range(min(len(feature_names), n_features_modelo)):
        nome = feature_names[i]
        print(f"  {nome}: {modelo_rf.feature_importances_[i]:.3f}")
    
    # Relatório SHAP para casos clonados
    print("\nExemplo de explicação SHAP para os primeiros casos clonados (formato amigável):")
    preds = modelo_rf.predict(X_teste)
    probs = modelo_rf.predict_proba(X_teste)
    traducao = {
        "dist_km": "Distância entre câmeras (km)",
        "delta_t_segundos": "Tempo entre leituras (segundos)",
        "velocidade_kmh": "Velocidade estimada (km/h)",
        "num_infracoes": "Número de infrações",
        "marca_modelo_igual": "Marca/modelo iguais",
        "tipo_igual": "Tipo igual",
        "cor_igual": "Cor igual"
    }
    
    clonados_exibidos = 0
    col_widths = [38, 12, 12, 22]
    
    def fmt_cell(val, width, align='center'):
        val_str = str(val)
        if align == 'center':
            return val_str.center(width)
        elif align == 'right':
            return val_str.rjust(width)
        else:
            return val_str.ljust(width)
    
    header = ["Característica", "Valor", "Impacto SHAP", "Interpretação"]
    print("|" + "|".join([fmt_cell(h, w) for h, w in zip(header, col_widths)]) + "|")
    print("|" + "|".join(["-"*w for w in col_widths]) + "|")
    
    total_clonados = np.sum(preds == 1)
    for idx in range(len(X_teste)):
        if preds[idx] != 1:
            continue
        clonados_exibidos += 1
        if clonados_exibidos > max_casos_exibidos:
            break
        
        # Calcular escore de suspeição (probabilidade da classe "clonado")
        escore_suspeicao = probs[idx][1] * 100  # Probabilidade da classe 1 (clonado) em porcentagem
        print(f"\nCaso {idx+1} - Predição: CLONADO - Escore de suspeição: {escore_suspeicao:.2f}%")
        print("|" + "|".join([fmt_cell(h, w) for h, w in zip(header, col_widths)]) + "|")
        print("|" + "|".join(["-"*w for w in col_widths]) + "|")
        
        shap_vals = shap_values[1][idx] if isinstance(shap_values, list) else shap_values[idx]
        feat_vals = X_teste[idx]
        resumo = []
        
        # Usar interpretação dinâmica baseada na distribuição dos valores SHAP deste caso
        for i, nome in enumerate(feature_names):
            nome_pt = traducao.get(nome, nome)
            valor = f"{feat_vals[i]:.3f}"
            impacto_raw = shap_vals[i]
            if isinstance(impacto_raw, (np.ndarray, list)):
                impacto_val = impacto_raw[1] if len(impacto_raw) > 1 else impacto_raw[0]
            else:
                impacto_val = impacto_raw
            impacto_fmt = f"{impacto_val:.3f}"
            
            # Usar interpretação dinâmica
            interpretacao = interpretar_impacto_shap_dinamico(impacto_val, shap_vals)
            # Extrai emoji e texto sem cortar a 1ª letra
            partes = interpretacao.split(' ', 1)
            emoji = partes[0] if partes else ''
            interpret = partes[1] if len(partes) > 1 else ''
            
            # Gerar resumo baseado na interpretação dinâmica
            if "Alto impacto" in interpretacao:
                if nome == "num_infracoes":
                    resumo.append("O número de infrações teve forte influência na decisão de clonagem.")
                elif nome in ["marca_modelo_igual", "tipo_igual", "cor_igual"]:
                    resumo.append(f"A similaridade de {nome_pt.lower()} teve forte influência na decisão de clonagem.")
                else:
                    resumo.append(f"{nome_pt} teve forte influência na decisão.")
            elif "Impacto moderado" in interpretacao:
                if nome == "num_infracoes":
                    resumo.append("O número de infrações teve impacto moderado na decisão.")
                elif nome in ["marca_modelo_igual", "tipo_igual", "cor_igual"]:
                    resumo.append(f"A similaridade de {nome_pt.lower()} teve impacto moderado na decisão.")
            
            print("|" +
                  fmt_cell(nome_pt, col_widths[0], 'left') + "|" +
                  fmt_cell(valor, col_widths[1], 'right') + "|" +
                  fmt_cell(impacto_fmt, col_widths[2], 'right') + "|" +
                  fmt_cell(f"{emoji} {interpret}", col_widths[3], 'left') + "|")
        
        if resumo:
            print("Resumo: " + " ".join(resumo))
        else:
            print("Resumo: Nenhuma característica teve impacto relevante para indicar clonagem.")
    
    if clonados_exibidos == 0:
        print(f"Nenhum caso clonado foi exibido. Total de predições clonadas: {total_clonados}")

def balancear_com_smote_binario(X_treino, X_treino_multimodal, y_treino, features_multimodal, config=None):
    """
    Aplica balanceamento SMOTE binário nos dados de treino.
    Retorna os dados balanceados ou originais se não for possível balancear.
    """
    # Calcular número de amostras por classe
    if SMOTE is None:
        print("⚠️ imbalanced-learn não instalado. Dados não balanceados.")
        print(f"✅ Dados de treino preparados:")
        print(f"   📊 {len(X_treino):,} pares de eventos")
        for classe in [0, 1]:
            print(f"   Classe {classe}: {np.sum(y_treino == classe)} exemplos")
        if len(features_multimodal) > 0:
            print(f"   🧬 Média de semelhança: {np.mean([f[-1] for f in features_multimodal]):.3f}")
        else:
            print(f"   🧬 Média de semelhança: N/A")
        return X_treino, X_treino_multimodal, y_treino
    unique, counts = np.unique(y_treino, return_counts=True)
    min_class_count = np.min(counts) if len(counts) > 0 else 0
    # Só aplica SMOTE se todas as classes tiverem pelo menos 2 exemplos
    if np.all(counts >= 2):
        # Usar k_neighbors do config ou valor padrão
        k_neighbors_config = config.get("smote_k_neighbors", 5) if config else 5
        k_neighbors = max(1, min(min_class_count - 1, k_neighbors_config))
        
        smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
        X_treino_bal, y_treino_bal = smote.fit_resample(X_treino, y_treino)
        X_treino_multimodal_bal, y_treino_multimodal_bal = smote.fit_resample(X_treino_multimodal, y_treino)
        print(f"✅ Dados balanceados com SMOTE (k_neighbors={k_neighbors}):")
        print(f"   📊 {len(X_treino_bal):,} pares de eventos (tradicional)")
        print(f"   📊 {len(X_treino_multimodal_bal):,} pares de eventos (multimodal)")
        # Contagem por classe
        for classe in [0, 1]:
            print(f"   Classe {classe}: {np.sum(y_treino_bal == classe)} exemplos")
        if len(X_treino_multimodal_bal) > 0:
            print(f"   🧬 Média de semelhança: {np.mean([f[-1] for f in X_treino_multimodal_bal]):.3f}")
        else:
            print(f"   🧬 Média de semelhança: N/A")
        return X_treino_bal, X_treino_multimodal_bal, y_treino_bal
    else:
        print("⚠️ SMOTE não aplicado: pelo menos uma classe tem menos de 2 exemplos.")
        print(f"✅ Dados de treino preparados (sem balanceamento):")
        print(f"   📊 {len(X_treino):,} pares de eventos")
        for classe in [0, 1]:
            print(f"   Classe {classe}: {np.sum(y_treino == classe)} exemplos")
        if len(features_multimodal) > 0:
            print(f"   🧬 Média de semelhança: {np.mean([f[-1] for f in features_multimodal]):.3f}")
        else:
            print(f"   🧬 Média de semelhança: N/A")
        return X_treino, X_treino_multimodal, y_treino

def main(config=None):
    """Função principal do teste."""
    print("🚀 INICIANDO TESTE DE MODELOS TEMPORAIS")
    print("=" * 60)
    
    # Se config não foi passado, carregar do arquivo
    if config is None:
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            print("⚠️ Arquivo config.json não encontrado")
            config = {}
    

    try:
        # 1. Inicializar simulador
        simulador = SimuladorStreamingALPR("config.json")
        eventos = simulador.executar_simulacao_completa()

        if not eventos:
            print("❌ Nenhum evento gerado pelo simulador")
            return

        # 1b. Aplicar pseudonimização se configurado
        if config and config.get("usar_pseudonimizacao", False):
            print("\n🔒 APLICANDO PSEUDONIMIZAÇÃO...")
            eventos = aplicar_pseudonimizacao_eventos(eventos, config)
        else:
            print("ℹ️ Pseudonimização desabilitada ou não configurada")

        # 2. Simular mudanças temporais
        fases = simular_mudancas_temporais(simulador, config)

        if not fases:
            print("❌ Erro ao criar fases temporais")
            return

        # 3. Preparar dados de treino inicial (fase 1)
        n_jobs = config.get("n_jobs", 8)
        X_treino, X_treino_multimodal, y_treino = preparar_dados_treino_inicial(fases[0], n_jobs, config)

        if len(X_treino) == 0:
            print("❌ Nenhum dado de treino gerado")
            return

        # 4. Inicializar comparador
        comparador = ComparadorModelos(simulador, n_jobs=n_jobs)

        # 5. Checagem de shapes antes do treino
        print(f"\n🔎 Shape X_treino: {X_treino.shape}, Shape X_treino_multimodal: {X_treino_multimodal.shape}, Shape y_treino: {y_treino.shape}")
        if X_treino.shape[0] != y_treino.shape[0]:
            print(f"❌ Inconsistência: X_treino tem {X_treino.shape[0]} linhas, y_treino tem {y_treino.shape[0]} labels. Treino abortado.")
            return
        print("\n🌟 Treinando modelo tradicional (apenas features básicas)...")
        comparador.treinar_modelo_tradicional(X_treino, y_treino, multimodal=False)
        print("\n🌟 Treinando modelo tradicional (multimodal: infrações + semelhança)...")
        comparador.treinar_modelo_tradicional(X_treino_multimodal, y_treino, multimodal=True)

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
                    comparador.processar_janela_adaptativo(janela_eventos, multimodal=False)
                    comparador.processar_janela_adaptativo(janela_eventos, multimodal=True)

                # Avaliar todos os modelos e salvar métricas para todos cenários
                comparador.avaliar_janela(janela_eventos, janela_contador, multimodal=False)
                comparador.avaliar_janela(janela_eventos, janela_contador, multimodal=True)

                janela_contador += 1

        # 7. Gerar relatório final (inclui precisão, recall, f1 para todos cenários)
        comparador.gerar_relatorio_final()

        # 7b. Explicabilidade XAI usando SHAP para o modelo tradicional
        try:
            import shap
        except ImportError:
            print("Instalando pacote SHAP...")
            import subprocess; subprocess.check_call(["pip", "install", "shap"])
            import shap

        modelo_rf = getattr(comparador, "modelo_tradicional_multimodal", None)
        if modelo_rf is not None:
            if len(fases) > 0 and len(fases[-1]) > 0:
                gerar_relatorio_xai_shap(modelo_rf, fases[-1], "🔎 EXPLICABILIDADE (XAI) PARA RANDOM FOREST TRADICIONAL MULTIMODAL:")
            else:
                print("Sem dados de teste para explicação XAI.")
        else:
            print("Modelo tradicional multimodal não encontrado para XAI.")

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
        modelo_rf = getattr(comparador, "modelo_tradicional_multimodal", None)
        if modelo_rf is not None:
            eventos_streaming = []
            janelas_stream = simulador.streaming_janelas_temporais(tamanho_janela_horas=2.0)
            for janela_eventos in janelas_stream:
                eventos_streaming.extend(janela_eventos)
            if len(eventos_streaming) == 0:
                print("Sem eventos de streaming para explicação XAI.")
                return
            gerar_relatorio_xai_shap(modelo_rf, eventos_streaming, "🔎 EXPLICABILIDADE (XAI) PARA CASOS CLONADOS DO STREAMING (MULTIMODAL):")
        
    except Exception as e:
        print(f"❌ Erro no teste de streaming: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando análise de modelos temporais para detecção de clonagem")
    print("=" * 70)
    
    # Carregar configuração
    config = None
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("⚠️ Arquivo config.json não encontrado. Usando configuração padrão.")
        config = {
            "usar_smote": False,
            "smote_k_neighbors": 5,
            "usar_pseudonimizacao": False,
            "salt_pseudonimizacao": "mopred_doutorado_2024_chave_secreta"
        }
    
    main(config)
