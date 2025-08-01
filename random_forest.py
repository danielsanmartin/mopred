"""
Detecção de Veículos Clonados usando Random Forest
==================================================

Protótipo para detecção de veículos clonados com base em dados ALPR simulados.
Utiliza Random Forest para classificar pares de capturas como suspeitos ou não.

Autor: Sistema de Detecção ALPR
Data: 2025
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from haversine import haversine
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

# =========================
# 1. Carregamento de dados ALPR
# =========================

def carregar_dados_alpr(caminho_arquivo="passagens.csv"):
    """
    Carrega dados ALPR de um arquivo CSV gerado pelo simulador.
    
    Args:
        caminho_arquivo: Caminho para o arquivo CSV das passagens
        
    Returns:
        DataFrame: Dados carregados ou None se houver erro
    """
    try:
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
        
        df = pd.read_csv(caminho_arquivo)
        print(f"✅ Dados carregados: {len(df):,} passagens de {caminho_arquivo}")
        print(f"   🏷️ Placas únicas: {df['placa'].nunique():,}")
        print(f"   📡 Câmeras: {df['cam'].nunique()}")
        
        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['placa', 'cam', 'timestamp', 'lat', 'lon']
        colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltando:
            raise ValueError(f"Colunas obrigatórias não encontradas: {colunas_faltando}")
        
        # Renomear timestamp para ts para compatibilidade
        if 'timestamp' in df.columns and 'ts' not in df.columns:
            df['ts'] = df['timestamp']
        
        # Converter timestamp para milissegundos se necessário
        if df['ts'].dtype != 'int64':
            print("⚠️ Convertendo timestamps para milissegundos...")
            df['ts'] = pd.to_datetime(df['ts']).astype(int) // 10**6
        
        # Estatísticas temporais
        inicio = pd.to_datetime(df['ts'], unit='ms').min()
        fim = pd.to_datetime(df['ts'], unit='ms').max()
        duracao = fim - inicio
        
        print(f"   📅 Período: {inicio.strftime('%Y-%m-%d %H:%M')} até {fim.strftime('%Y-%m-%d %H:%M')}")
        print(f"   ⏱️ Duração: {duracao.total_seconds()/3600:.1f} horas")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados ALPR: {e}")
        return None

def carregar_veiculos_info(caminho_arquivo="veiculos_gerados.csv"):
    """
    Carrega informações dos veículos para identificar quais são clonados.
    
    Args:
        caminho_arquivo: Caminho para o arquivo de veículos
        
    Returns:
        DataFrame: Informações dos veículos ou None se não encontrado
    """
    try:
        if not os.path.exists(caminho_arquivo):
            print(f"⚠️ Arquivo de veículos não encontrado: {caminho_arquivo}")
            print("   Continuando sem informação de veículos clonados...")
            return None
        
        df_veiculos = pd.read_csv(caminho_arquivo)
        print(f"✅ Informações de veículos carregadas: {len(df_veiculos):,} veículos")
        
        if 'clonado' in df_veiculos.columns:
            clonados = df_veiculos[df_veiculos['clonado'] == 1]
            print(f"   ⚠️ Veículos clonados identificados: {len(clonados)}")
            return df_veiculos
        else:
            print("   ⚠️ Coluna 'clonado' não encontrada no arquivo de veículos")
            return None
            
    except Exception as e:
        print(f"⚠️ Erro ao carregar informações de veículos: {e}")
        return None

def simular_dados_alpr():
    """
    Função mantida por compatibilidade. Agora carrega dados reais do CSV.
    """
    print("🔄 Carregando dados das passagens ALPR...")
    return carregar_dados_alpr("passagens.csv")

# =========================
# 2. Engenharia de Features
# =========================

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre dois pontos usando a fórmula de Haversine.
    
    Args:
        lat1, lon1: Coordenadas do primeiro ponto
        lat2, lon2: Coordenadas do segundo ponto
    
    Returns:
        float: Distância em quilômetros
    """
    return haversine((lat1, lon1), (lat2, lon2))

def calcular_velocidade_teorica(dist_km, tempo_segundos):
    """
    Calcula a velocidade teórica necessária para percorrer uma distância em um tempo.
    
    Args:
        dist_km: Distância em quilômetros
        tempo_segundos: Tempo em segundos
    
    Returns:
        float: Velocidade em km/h
    """
    if tempo_segundos <= 0:
        return 9999.0  # Velocidade impossível para tempo zero ou negativo
    
    tempo_horas = tempo_segundos / 3600
    return dist_km / tempo_horas

def gerar_pares_features(df, df_veiculos=None, limiar_velocidade=150, max_pares_por_placa=50):
    """
    Gera pares de capturas da mesma placa em câmeras diferentes e extrai features.
    Para veículos clonados, cada passagem pode representar um clone diferente.
    
    Args:
        df: DataFrame com dados ALPR
        df_veiculos: DataFrame com informações dos veículos (incluindo flag clonado)
        limiar_velocidade: Velocidade limite para classificar como suspeito (km/h)
        max_pares_por_placa: Limite máximo de pares por placa para evitar explosão combinatória
    
    Returns:
        tuple: (features_array, labels_array, pares_info)
    """
    features = []
    labels = []
    pares_info = []
    
    # Criar set de placas clonadas se informação disponível
    placas_clonadas = set()
    if df_veiculos is not None and 'clonado' in df_veiculos.columns:
        placas_clonadas = set(df_veiculos[df_veiculos['clonado'] == 1]['placa'])
        print(f"🔍 Placas clonadas identificadas: {len(placas_clonadas)}")
    
    placas_unicas = df['placa'].unique()
    print(f"🔍 Analisando {len(placas_unicas):,} placas para gerar pares...")
    
    total_pares = 0
    placas_processadas = 0
    
    for placa in placas_unicas:
        eventos_placa = df[df['placa'] == placa].sort_values(by='ts').reset_index(drop=True)
        
        # Verificar se a placa é conhecidamente clonada
        is_placa_clonada = placa in placas_clonadas
        
        # Limitar número de eventos por placa para evitar explosão combinatória
        if len(eventos_placa) > 20:
            eventos_placa = eventos_placa.sample(n=20, random_state=42).sort_values(by='ts').reset_index(drop=True)
        
        pares_placa = 0
        
        if is_placa_clonada:
            # ESTRATÉGIA PARA PLACAS CLONADAS:
            # Cada passagem pode ser de um clone diferente, então analisamos todos os pares
            print(f"   🚨 Analisando placa clonada: {placa} ({len(eventos_placa)} passagens)")
            
            for i in range(len(eventos_placa)):
                if pares_placa >= max_pares_por_placa:
                    break
                    
                for j in range(i + 1, len(eventos_placa)):
                    if pares_placa >= max_pares_por_placa:
                        break
                        
                    evento1 = eventos_placa.iloc[i]
                    evento2 = eventos_placa.iloc[j]
                    
                    # Pular pares da mesma câmera
                    if evento1['cam'] == evento2['cam']:
                        continue
                    
                    # Processar par e adicionar aos dados
                    if processar_par_eventos(evento1, evento2, placa, True, limiar_velocidade, 
                                           features, labels, pares_info):
                        pares_placa += 1
                        total_pares += 1
        else:
            # ESTRATÉGIA PARA PLACAS NORMAIS:
            # Analisar principalmente pares consecutivos e alguns aleatórios
            
            # 1. Pares consecutivos (comportamento normal esperado)
            for i in range(len(eventos_placa) - 1):
                if pares_placa >= max_pares_por_placa // 2:  # Reserva metade para consecutivos
                    break
                    
                evento1 = eventos_placa.iloc[i]
                evento2 = eventos_placa.iloc[i + 1]
                
                # Pular pares da mesma câmera
                if evento1['cam'] == evento2['cam']:
                    continue
                
                # Processar par consecutivo
                if processar_par_eventos(evento1, evento2, placa, False, limiar_velocidade,
                                       features, labels, pares_info):
                    pares_placa += 1
                    total_pares += 1
            
            # 2. Alguns pares não-consecutivos para detectar comportamentos anômalos
            if len(eventos_placa) > 2:
                import random
                pares_extras = min(max_pares_por_placa - pares_placa, len(eventos_placa) // 2)
                
                for _ in range(pares_extras):
                    if pares_placa >= max_pares_por_placa:
                        break
                        
                    # Escolher dois índices aleatórios não consecutivos
                    indices = list(range(len(eventos_placa)))
                    random.shuffle(indices)
                    
                    for i in range(len(indices) - 1):
                        for j in range(i + 1, len(indices)):
                            if abs(indices[i] - indices[j]) == 1:  # Pular consecutivos
                                continue
                                
                            evento1 = eventos_placa.iloc[indices[i]]
                            evento2 = eventos_placa.iloc[indices[j]]
                            
                            # Pular pares da mesma câmera
                            if evento1['cam'] == evento2['cam']:
                                continue
                            
                            # Processar par não-consecutivo
                            if processar_par_eventos(evento1, evento2, placa, False, limiar_velocidade,
                                                   features, labels, pares_info):
                                pares_placa += 1
                                total_pares += 1
                                break
                        if pares_placa >= max_pares_por_placa:
                            break
                    if pares_placa >= max_pares_por_placa:
                        break
        
        placas_processadas += 1
        if placas_processadas % 1000 == 0:
            print(f"   📈 Progresso: {placas_processadas:,}/{len(placas_unicas):,} placas "
                  f"({total_pares:,} pares gerados)")
    
    features_array = np.array(features)
    labels_array = np.array(labels)
    
    print(f"📊 Gerados {len(features):,} pares de capturas")
    print(f"   🚨 Suspeitos: {sum(labels):,} ({sum(labels)/len(labels)*100:.1f}%)")
    print(f"   ✅ Normais: {len(labels) - sum(labels):,} ({(len(labels) - sum(labels))/len(labels)*100:.1f}%)")
    
    # Estatísticas por velocidade
    velocidades = [par['velocidade_kmh'] for par in pares_info]
    print(f"   📊 Velocidade média: {np.mean(velocidades):.1f} km/h")
    print(f"   📊 Velocidade máxima: {np.max(velocidades):.1f} km/h")
    print(f"   📊 Velocidades > 200 km/h: {sum(1 for v in velocidades if v > 200):,}")
    
    return features_array, labels_array, pares_info


def processar_par_eventos(evento1, evento2, placa, is_placa_clonada, limiar_velocidade, 
                         features, labels, pares_info):
    """
    Processa um par de eventos e adiciona às listas de features/labels.
    
    Args:
        evento1, evento2: Eventos a serem comparados
        placa: Placa do veículo
        is_placa_clonada: Se a placa é conhecidamente clonada
        limiar_velocidade: Limite de velocidade para classificar como suspeito
        features, labels, pares_info: Listas para adicionar os resultados
        
    Returns:
        bool: True se o par foi processado com sucesso
    """
    # Calcular features
    dist_km = calcular_distancia_haversine(
        evento1['lat'], evento1['lon'],
        evento2['lat'], evento2['lon']
    )
    
    delta_t_ms = abs(evento2['ts'] - evento1['ts'])
    delta_t_segundos = delta_t_ms / 1000
    
    # Pular pares com tempo muito pequeno (menos de 30 segundos)
    if delta_t_segundos < 30:
        return False
    
    velocidade_teorica = calcular_velocidade_teorica(dist_km, delta_t_segundos)
    
    # Features para o modelo
    feature_vector = [dist_km, delta_t_segundos, velocidade_teorica]
    features.append(feature_vector)
    
    # Determinar label baseado na lógica de clonagem
    if is_placa_clonada:
        # Para placas conhecidamente clonadas, usar critérios mais rigorosos
        # Velocidade alta OU distância grande em tempo curto
        label = 1 if (velocidade_teorica > limiar_velocidade or 
                     (dist_km > 50 and delta_t_segundos < 3600)) else 0
    else:
        # Para placas normais, usar apenas velocidade como critério principal
        label = 1 if velocidade_teorica > limiar_velocidade else 0
    
    labels.append(label)
    
    # Informações do par para debugging
    par_info = {
        'placa': placa,
        'cam1': evento1['cam'],
        'cam2': evento2['cam'],
        'ts1': evento1['ts'],
        'ts2': evento2['ts'],
        'dist_km': round(dist_km, 2),
        'delta_t_segundos': round(delta_t_segundos, 0),
        'velocidade_kmh': round(velocidade_teorica, 1),
        'suspeito': label == 1,
        'placa_clonada': is_placa_clonada,
        'timestamp1_legivel': pd.to_datetime(evento1['ts'], unit='ms').strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp2_legivel': pd.to_datetime(evento2['ts'], unit='ms').strftime('%Y-%m-%d %H:%M:%S'),
        'tipo_par': 'clonado' if is_placa_clonada else 'normal'
    }
    pares_info.append(par_info)
    
    return True

# =========================
# 3. Treinamento e Avaliação do Modelo
# =========================

def treinar_modelo_random_forest(X, y, test_size=0.3, random_state=42):
    """
    Treina um modelo Random Forest para classificação de veículos clonados.
    
    Args:
        X: Array de features
        y: Array de labels
        test_size: Proporção dos dados para teste
        random_state: Seed para reprodutibilidade
    
    Returns:
        tuple: (modelo_treinado, dados_teste)
    """
    print("🤖 Iniciando treinamento do modelo Random Forest...")
    
    # Verificar se temos dados suficientes
    if len(X) < 10:
        print("⚠️ Poucos dados para divisão treino/teste. Usando validação cruzada simples.")
        test_size = 0.2
    
    # Verificar balanceamento das classes
    unique, counts = np.unique(y, return_counts=True)
    print(f"   📊 Distribuição das classes: {dict(zip(unique, counts))}")
    
    # Dividir dados
    stratify = y if len(unique) > 1 and min(counts) > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )
    
    # Configurar e treinar modelo
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=random_state,
        class_weight='balanced',  # Para lidar com desbalanceamento
        min_samples_split=5,
        min_samples_leaf=2
    )
    
    modelo.fit(X_train, y_train)
    
    print(f"✅ Modelo treinado com {len(X_train):,} amostras")
    print(f"   📊 Features: dist_km, delta_t_segundos, velocidade_teorica")
    print(f"   ⚖️ Classes balanceadas automaticamente")
    
    return modelo, (X_train, X_test, y_train, y_test)

def avaliar_modelo(modelo, dados_teste):
    """
    Avalia o desempenho do modelo com métricas detalhadas.
    
    Args:
        modelo: Modelo treinado
        dados_teste: Tupla com (X_train, X_test, y_train, y_test)
    """
    X_train, X_test, y_train, y_test = dados_teste
    
    print("\n" + "="*50)
    print("📈 AVALIAÇÃO DO MODELO")
    print("="*50)
    
    # Predições
    y_pred_train = modelo.predict(X_train)
    y_pred_test = modelo.predict(X_test)
    
    # Métricas de treino
    print("\n🎯 DESEMPENHO NO CONJUNTO DE TREINO:")
    print(f"   Accuracy: {accuracy_score(y_train, y_pred_train):.3f}")
    
    # Métricas de teste
    print("\n🎯 DESEMPENHO NO CONJUNTO DE TESTE:")
    print(f"   Accuracy:  {accuracy_score(y_test, y_pred_test):.3f}")
    print(f"   Precision: {precision_score(y_test, y_pred_test, average='weighted', zero_division=0):.3f}")
    print(f"   Recall:    {recall_score(y_test, y_pred_test, average='weighted', zero_division=0):.3f}")
    print(f"   F1-Score:  {f1_score(y_test, y_pred_test, average='weighted', zero_division=0):.3f}")
    
    # Matriz de confusão
    print("\n📊 MATRIZ DE CONFUSÃO:")
    cm = confusion_matrix(y_test, y_pred_test)
    print(cm)
    print("   [0,0]: Verdadeiros Negativos (Normal classificado como Normal)")
    print("   [0,1]: Falsos Positivos (Normal classificado como Suspeito)")  
    print("   [1,0]: Falsos Negativos (Suspeito classificado como Normal)")
    print("   [1,1]: Verdadeiros Positivos (Suspeito classificado como Suspeito)")
    
    # Relatório de classificação detalhado
    print("\n📋 RELATÓRIO DE CLASSIFICAÇÃO:")
    print(classification_report(y_test, y_pred_test, target_names=['Normal', 'Suspeito'], zero_division=0))
    
    # Importância das features
    print("\n🔍 IMPORTÂNCIA DAS FEATURES:")
    feature_names = ['Distância (km)', 'Tempo (seg)', 'Velocidade (km/h)']
    importancias = modelo.feature_importances_
    for nome, importancia in zip(feature_names, importancias):
        print(f"   {nome}: {importancia:.3f}")

# =========================
# 4. Função de Predição para Novos Eventos
# =========================

def prever_evento(modelo, captura1, captura2, mostrar_detalhes=True):
    """
    Prevê se um par de capturas indica possível clonagem de veículo.
    
    Args:
        modelo: Modelo Random Forest treinado
        captura1: Dict com dados da primeira captura {'lat', 'lon', 'ts'}
        captura2: Dict com dados da segunda captura {'lat', 'lon', 'ts'}
        mostrar_detalhes: Se deve imprimir detalhes do cálculo
    
    Returns:
        tuple: (predicao, probabilidade, detalhes)
    """
    # Calcular features
    dist_km = calcular_distancia_haversine(
        captura1['lat'], captura1['lon'],
        captura2['lat'], captura2['lon']
    )
    
    delta_t_ms = abs(captura2['ts'] - captura1['ts'])
    delta_t_segundos = delta_t_ms / 1000
    
    velocidade_teorica = calcular_velocidade_teorica(dist_km, delta_t_segundos)
    
    # Preparar entrada para o modelo
    features_entrada = np.array([[dist_km, delta_t_segundos, velocidade_teorica]])
    
    # Fazer predição
    predicao = modelo.predict(features_entrada)[0]
    probabilidades = modelo.predict_proba(features_entrada)[0]
    probabilidade_suspeito = probabilidades[1] if len(probabilidades) > 1 else 0.0
    
    # Detalhes do cálculo
    detalhes = {
        'distancia_km': dist_km,
        'tempo_segundos': delta_t_segundos,
        'velocidade_kmh': velocidade_teorica,
        'predicao': predicao,
        'probabilidade_suspeito': probabilidade_suspeito
    }
    
    if mostrar_detalhes:
        print(f"\n🔍 ANÁLISE DO PAR DE CAPTURAS:")
        print(f"   Distância: {dist_km:.2f} km")
        print(f"   Tempo: {delta_t_segundos:.0f} segundos ({delta_t_segundos/60:.1f} minutos)")
        print(f"   Velocidade teórica: {velocidade_teorica:.1f} km/h")
        print(f"   Predição: {'SUSPEITO' if predicao == 1 else 'NORMAL'}")
        print(f"   Probabilidade de clonagem: {probabilidade_suspeito:.2f}")
        print(f"   Alerta: {'🚨 SIM' if predicao == 1 else '✅ NÃO'}")
    
    return predicao, probabilidade_suspeito, detalhes

# =========================
# 5. Função Principal e Exemplos de Uso
# =========================

def main():
    """
    Função principal que executa todo o pipeline de detecção de veículos clonados.
    """
    print("🚗 SISTEMA DE DETECÇÃO DE VEÍCULOS CLONADOS")
    print("=" * 60)
    
    # 1. Carregar dados das passagens
    df = carregar_dados_alpr("passagens.csv")
    if df is None or len(df) == 0:
        print("❌ Não foi possível carregar dados de passagens. Encerrando.")
        return None, None, None
    
    # 2. Carregar informações dos veículos (opcional)
    df_veiculos = carregar_veiculos_info("veiculos_gerados.csv")
    
    # 3. Gerar features e labels
    print("\n🔧 Gerando features dos pares de capturas...")
    X, y, pares_info = gerar_pares_features(df, df_veiculos, limiar_velocidade=150)
    
    if len(X) == 0:
        print("❌ Nenhum par de capturas gerado. Verifique os dados.")
        return None, None, None
    
    # 4. Treinar modelo
    modelo, dados_teste = treinar_modelo_random_forest(X, y)
    
    # 5. Avaliar modelo
    avaliar_modelo(modelo, dados_teste)
    
    # 6. Mostrar alguns exemplos dos pares analisados
    print("\n" + "="*60)
    print("📋 EXEMPLOS DE PARES ANALISADOS:")
    print("="*60)
    
    # Ordenar por velocidade decrescente para mostrar casos mais suspeitos
    pares_ordenados = sorted(pares_info, key=lambda x: x['velocidade_kmh'], reverse=True)
    
    print("\n🚨 TOP 5 CASOS MAIS SUSPEITOS (maior velocidade):")
    for i, par in enumerate(pares_ordenados[:5]):
        status = "🚨 SUSPEITO" if par['suspeito'] else "✅ NORMAL"
        clonado_info = f" ({'CLONADO' if par['placa_clonada'] else 'NORMAL'})" if 'placa_clonada' in par else ""
        print(f"\n{i+1}. Placa {par['placa']}{clonado_info} - {status}")
        print(f"   {par['cam1']} → {par['cam2']}")
        print(f"   {par['timestamp1_legivel']} → {par['timestamp2_legivel']}")
        print(f"   Distância: {par['dist_km']:.2f} km")
        print(f"   Tempo: {par['delta_t_segundos']:.0f}s ({par['delta_t_segundos']/60:.1f} min)")
        print(f"   Velocidade: {par['velocidade_kmh']:.1f} km/h")
    
    # 7. Exemplos de predição para novos eventos
    print("\n" + "="*60)
    print("🔮 EXEMPLOS DE PREDIÇÃO PARA NOVOS EVENTOS:")
    print("="*60)
    
    # Usar timestamps realistas baseados nos dados carregados
    timestamp_base = int(df['ts'].min())
    
    # Exemplo 1: Caso suspeito (velocidade alta)
    print("\n1️⃣ EXEMPLO SUSPEITO:")
    evento1 = {"lat": -27.5954, "lon": -48.5480, "ts": timestamp_base}
    evento2 = {"lat": -27.6954, "lon": -48.5580, "ts": timestamp_base + 200000}  # 200 segundos depois
    prever_evento(modelo, evento1, evento2)
    
    # Exemplo 2: Caso normal (velocidade aceitável)
    print("\n2️⃣ EXEMPLO NORMAL:")
    evento3 = {"lat": -27.5954, "lon": -48.5480, "ts": timestamp_base}
    evento4 = {"lat": -27.6000, "lon": -48.5490, "ts": timestamp_base + 1800000}  # 30 minutos depois
    prever_evento(modelo, evento3, evento4)
    
    # Exemplo 3: Caso limítrofe
    print("\n3️⃣ EXEMPLO LIMÍTROFE:")
    evento5 = {"lat": -27.5954, "lon": -48.5480, "ts": timestamp_base}
    evento6 = {"lat": -27.6200, "lon": -48.5600, "ts": timestamp_base + 600000}  # 10 minutos depois
    prever_evento(modelo, evento5, evento6)
    
    print("\n" + "="*60)
    print("✅ ANÁLISE CONCLUÍDA!")
    print("="*60)
    
    return modelo, df, pares_info

def carregar_dados_csv(caminho_arquivo):
    """
    Função mantida por compatibilidade. Redireciona para carregar_dados_alpr.
    """
    return carregar_dados_alpr(caminho_arquivo)

def salvar_resultados_csv(pares_info, caminho_saida="resultados_analise.csv"):
    """
    Salva os resultados da análise em um arquivo CSV.
    
    Args:
        pares_info: Lista com informações dos pares analisados
        caminho_saida: Caminho do arquivo de saída
    """
    try:
        df_resultados = pd.DataFrame(pares_info)
        df_resultados.to_csv(caminho_saida, index=False, encoding='utf-8')
        print(f"💾 Resultados salvos em: {caminho_saida}")
        
        # Estatísticas do arquivo salvo
        suspeitos = len(df_resultados[df_resultados['suspeito'] == True])
        print(f"   📊 Total de pares: {len(df_resultados):,}")
        print(f"   🚨 Casos suspeitos: {suspeitos:,} ({suspeitos/len(df_resultados)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Erro ao salvar resultados: {e}")

# =========================
# 6. Execução do Programa
# =========================

if __name__ == "__main__":
    # Executar análise completa
    resultado = main()
    
    if resultado[0] is not None:  # Se o modelo foi treinado com sucesso
        modelo_treinado, dados_originais, resultados_pares = resultado
        
        # Salvar resultados (opcional)
        salvar_resultados_csv(resultados_pares, "analise_clonagem_veiculos.csv")
        
        print("\n💡 DICAS DE USO:")
        print("- O programa agora lê dados do arquivo 'passagens.csv'")
        print("- Para usar outros arquivos: carregar_dados_alpr('seu_arquivo.csv')")
        print("- Para predições individuais: prever_evento(modelo, evento1, evento2)")
        print("- Ajuste o limiar de velocidade conforme necessário (padrão: 150 km/h)")
        print("- Os resultados são salvos em 'analise_clonagem_veiculos.csv'")
    else:
        print("❌ Não foi possível executar a análise. Verifique os arquivos de entrada.")
