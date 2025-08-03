import numpy as np
from haversine import haversine

def processar_placa_basico(eventos_placa):
    features = []
    features_semelhanca = []
    labels = []
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
        semelhanca = evento1.get('semelhanca', 1.0)
        feature_vector = [dist_km, delta_t_segundos, velocidade_kmh]
        features.append(feature_vector)
        feature_vector_semelhanca = [dist_km, delta_t_segundos, velocidade_kmh, num_infracoes, semelhanca]
        features_semelhanca.append(feature_vector_semelhanca)
        is_suspeito = velocidade_kmh > 200 or evento1.get('is_clonado', False)
        labels.append(1 if is_suspeito else 0)
    # Retorno compatível com pipeline: features, labels, features_semelhanca
    return features, labels, features_semelhanca
