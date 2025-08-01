"""
Comparador de Random Forest Tradicional vs. Adaptativo
======================================================

Compara o desempenho de modelos Random Forest em dados com mudanças temporais.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from haversine import haversine
from river import ensemble, tree, forest
import warnings
warnings.filterwarnings('ignore')

# Usando River para Random Forest Adaptativo real
class AdaptiveRandomForestWrapper:
    """Wrapper para o Random Forest Adaptativo do River."""
    
    def __init__(self, n_models=10, seed=42):
        # Usar ARFClassifier (Adaptive Random Forest) do módulo forest
        self.arf = forest.ARFClassifier(
            n_models=n_models,
            seed=seed,
            leaf_prediction="nba",  # Naive Bayes Adaptive
            nominal_attributes=None
        )
        self.initialized = False
        
    def learn_batch(self, X, y):
        """Aprende com um lote de dados."""
        if len(X) == 0:
            return
            
        # Treinar incrementalmente com cada amostra
        for i in range(len(X)):
            # Converter array numpy para dicionário (formato do River)
            x_dict = {f'feature_{j}': float(X[i][j]) for j in range(len(X[i]))}
            self.arf.learn_one(x_dict, int(y[i]))
        
        self.initialized = True
    
    def predict_batch(self, X):
        """Faz predições para um lote de dados."""
        if not self.initialized or len(X) == 0:
            return np.zeros(len(X))
        
        predictions = []
        for i in range(len(X)):
            x_dict = {f'feature_{j}': float(X[i][j]) for j in range(len(X[i]))}
            try:
                pred = self.arf.predict_one(x_dict)
                predictions.append(int(pred) if pred is not None else 0)
            except:
                predictions.append(0)
        
        return np.array(predictions)

class ComparadorModelos:
    def __init__(self, simulador_streaming):
        self.simulador = simulador_streaming
        self.modelo_tradicional = None
        self.modelo_tradicional_infracoes = None
        self.modelo_adaptativo = AdaptiveRandomForestWrapper(
            n_models=10,
            seed=42
        )
        self.historico_metricas = {
            'tradicional': [],
            'tradicional_infracoes': [],
            'adaptativo': [],
            'adaptativo_infracoes': []
        }
        
    def treinar_modelo_tradicional(self, X_treino, y_treino, usar_infracoes=False):
        """Treina o modelo Random Forest tradicional (com ou sem infrações)."""
        if usar_infracoes:
            print("🌳 Treinando Random Forest Tradicional (com infrações)...")
            self.modelo_tradicional_infracoes = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.modelo_tradicional_infracoes.fit(X_treino, y_treino)
            print(f"✅ Modelo tradicional (com infrações) treinado com {len(X_treino):,} amostras")
        else:
            print("🌳 Treinando Random Forest Tradicional...")
            self.modelo_tradicional = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.modelo_tradicional.fit(X_treino, y_treino)
            print(f"✅ Modelo tradicional treinado com {len(X_treino):,} amostras")
    
    def processar_janela_adaptativo(self, eventos_janela, usar_infracoes=False):
        """Processa uma janela de eventos para o modelo adaptativo. Se usar_infracoes=True, usa a feature de infrações."""
        if usar_infracoes:
            features, labels, _ = self._gerar_features_janela_infracoes(eventos_janela)
        else:
            features, labels, _ = self._gerar_features_janela(eventos_janela)

        if len(features) > 0:
            self.modelo_adaptativo.learn_batch(features, labels)

        return features, labels
    
    def avaliar_janela(self, eventos_janela, janela_numero, usar_infracoes=False):
        """Avalia ambos os modelos em uma janela de teste. Se usar_infracoes=True, avalia os modelos com a feature de infrações."""
        print(f"\n📊 Avaliando Janela {janela_numero} ({len(eventos_janela)} eventos)" + (" [com infrações]" if usar_infracoes else ""))

        # Gerar features para teste
        if usar_infracoes:
            X_teste, y_teste, pares_info = self._gerar_features_janela_infracoes(eventos_janela)
        else:
            X_teste, y_teste, pares_info = self._gerar_features_janela(eventos_janela)

        if len(X_teste) == 0:
            print("⚠️ Nenhum par válido gerado para esta janela")
            return None, None

        # Avaliar modelo tradicional
        metricas_tradicional = self._avaliar_tradicional(X_teste, y_teste, janela_numero, usar_infracoes=usar_infracoes)

        # Avaliar modelo adaptativo
        metricas_adaptativo = self._avaliar_adaptativo(X_teste, y_teste, janela_numero, usar_infracoes=usar_infracoes)

        # Armazenar métricas
        if usar_infracoes:
            self.historico_metricas['tradicional_infracoes'].append(metricas_tradicional)
            self.historico_metricas['adaptativo_infracoes'].append(metricas_adaptativo)
        else:
            self.historico_metricas['tradicional'].append(metricas_tradicional)
            self.historico_metricas['adaptativo'].append(metricas_adaptativo)

        # Imprimir comparação
        self._imprimir_comparacao(metricas_tradicional, metricas_adaptativo, janela_numero)

        return metricas_tradicional, metricas_adaptativo
    
    def _avaliar_tradicional(self, X_teste, y_teste, janela_numero, usar_infracoes=False):
        """Avalia o modelo tradicional (sem retreinamento). Se usar_infracoes=True, usa o modelo com infrações."""
        if usar_infracoes:
            if self.modelo_tradicional_infracoes is None:
                raise ValueError("Modelo tradicional (com infrações) não foi treinado")
            y_pred = self.modelo_tradicional_infracoes.predict(X_teste)
            tipo = 'tradicional_infracoes'
        else:
            if self.modelo_tradicional is None:
                raise ValueError("Modelo tradicional não foi treinado")
            y_pred = self.modelo_tradicional.predict(X_teste)
            tipo = 'tradicional'
        return {
            'janela': janela_numero,
            'accuracy': accuracy_score(y_teste, y_pred),
            'precision': precision_score(y_teste, y_pred, zero_division=0),
            'recall': recall_score(y_teste, y_pred, zero_division=0),
            'f1': f1_score(y_teste, y_pred, zero_division=0),
            'n_amostras': len(y_teste),
            'n_suspeitos': sum(y_teste),
            'tipo': tipo
        }
    def _gerar_features_janela_infracoes(self, eventos_janela):
        """Gera features para uma janela de eventos, incluindo num_infracoes."""
        eventos_dict = [evento.to_dict() for evento in eventos_janela]
        df_janela = pd.DataFrame(eventos_dict)
        if len(df_janela) == 0:
            return np.array([]), np.array([]), []
        df_janela['ts'] = df_janela['timestamp']
        features = []
        labels = []
        pares_info = []
        placas_unicas = df_janela['placa'].unique()
        for placa in placas_unicas:
            eventos_placa = df_janela[df_janela['placa'] == placa].sort_values('ts')
            if len(eventos_placa) < 2:
                continue
            for i in range(len(eventos_placa) - 1):
                evento1 = eventos_placa.iloc[i]
                evento2 = eventos_placa.iloc[i + 1]
                if evento1['cam'] == evento2['cam']:
                    continue
                dist_km = haversine(
                    (evento1['lat'], evento1['lon']),
                    (evento2['lat'], evento2['lon'])
                )
                delta_t_ms = abs(evento2['ts'] - evento1['ts'])
                delta_t_segundos = delta_t_ms / 1000
                if delta_t_segundos < 30:
                    continue
                velocidade_kmh = (dist_km / (delta_t_segundos / 3600)) if delta_t_segundos > 0 else 9999
                num_infracoes = evento1.get('num_infracoes', 0)
                feature_vector = [dist_km, delta_t_segundos, velocidade_kmh, num_infracoes]
                features.append(feature_vector)
                is_suspeito = velocidade_kmh > 150 or evento1.get('is_clonado', False)
                labels.append(1 if is_suspeito else 0)
                par_info = {
                    'placa': placa,
                    'dist_km': dist_km,
                    'delta_t_segundos': delta_t_segundos,
                    'velocidade_kmh': velocidade_kmh,
                    'num_infracoes': num_infracoes,
                    'is_clonado': evento1.get('is_clonado', False)
                }
                pares_info.append(par_info)
        return np.array(features), np.array(labels), pares_info
    
    def _avaliar_adaptativo(self, X_teste, y_teste, janela_numero, usar_infracoes=False):
        """Avalia o modelo adaptativo. Se usar_infracoes=True, marca o tipo corretamente."""
        y_pred = self.modelo_adaptativo.predict_batch(X_teste)
        tipo = 'adaptativo_infracoes' if usar_infracoes else 'adaptativo'
        return {
            'janela': janela_numero,
            'accuracy': accuracy_score(y_teste, y_pred),
            'precision': precision_score(y_teste, y_pred, zero_division=0),
            'recall': recall_score(y_teste, y_pred, zero_division=0),
            'f1': f1_score(y_teste, y_pred, zero_division=0),
            'n_amostras': len(y_teste),
            'n_suspeitos': sum(y_teste),
            'tipo': tipo
        }
    
    def _gerar_features_janela(self, eventos_janela):
        """Gera features para uma janela de eventos."""
        # Converter eventos para DataFrame
        eventos_dict = [evento.to_dict() for evento in eventos_janela]
        df_janela = pd.DataFrame(eventos_dict)
        
        if len(df_janela) == 0:
            return np.array([]), np.array([]), []
        
        # Renomear colunas para compatibilidade
        df_janela['ts'] = df_janela['timestamp']
        
        # Gerar pares de eventos da mesma placa
        features = []
        labels = []
        pares_info = []
        
        placas_unicas = df_janela['placa'].unique()
        
        for placa in placas_unicas:
            eventos_placa = df_janela[df_janela['placa'] == placa].sort_values('ts')
            
            if len(eventos_placa) < 2:
                continue
            
            # Gerar pares consecutivos
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
                
                delta_t_ms = abs(evento2['ts'] - evento1['ts'])
                delta_t_segundos = delta_t_ms / 1000
                
                # Pular pares com tempo muito pequeno
                if delta_t_segundos < 30:
                    continue
                
                velocidade_kmh = (dist_km / (delta_t_segundos / 3600)) if delta_t_segundos > 0 else 9999
                
                # Features para o modelo
                feature_vector = [dist_km, delta_t_segundos, velocidade_kmh]
                features.append(feature_vector)
                
                # Label baseado na velocidade e informação de clonagem
                is_suspeito = velocidade_kmh > 150 or evento1.get('is_clonado', False)
                labels.append(1 if is_suspeito else 0)
                
                # Informações do par
                par_info = {
                    'placa': placa,
                    'dist_km': dist_km,
                    'delta_t_segundos': delta_t_segundos,
                    'velocidade_kmh': velocidade_kmh,
                    'is_clonado': evento1.get('is_clonado', False)
                }
                pares_info.append(par_info)
        
        return np.array(features), np.array(labels), pares_info
    
    def _imprimir_comparacao(self, trad, adapt, janela_numero):
        """Imprime comparação das métricas."""
        print(f"┌─── Janela {janela_numero} - Comparação ───┐")
        print(f"│ Métrica    │ Tradicional │ Adaptativo │")
        print(f"├────────────┼─────────────┼────────────┤")
        print(f"│ Accuracy   │    {trad['accuracy']:.3f}    │   {adapt['accuracy']:.3f}    │")
        print(f"│ Precision  │    {trad['precision']:.3f}    │   {adapt['precision']:.3f}    │")
        print(f"│ Recall     │    {trad['recall']:.3f}    │   {adapt['recall']:.3f}    │")
        print(f"│ F1-Score   │    {trad['f1']:.3f}    │   {adapt['f1']:.3f}    │")
        print(f"└────────────┴─────────────┴────────────┘")
        
        # Destacar melhor performance
        melhor = "🔄 Adaptativo" if adapt['f1'] > trad['f1'] else "🏛️ Tradicional"
        if adapt['f1'] == trad['f1']:
            melhor = "🤝 Empate"
        print(f"Melhor F1-Score: {melhor}")
    
    def gerar_relatorio_final(self):
        """Gera relatório final da comparação."""
        print(f"\n📈 RELATÓRIO FINAL - COMPARAÇÃO DE MODELOS")
        print(f"=" * 60)
        
        if not self.historico_metricas['tradicional']:
            print("❌ Nenhuma métrica disponível para análise")
            return
        
        df_trad = pd.DataFrame(self.historico_metricas['tradicional'])
        df_adapt = pd.DataFrame(self.historico_metricas['adaptativo'])
        
        # Médias gerais
        print(f"\n📊 MÉDIAS GERAIS:")
        print(f"Random Forest Tradicional:")
        print(f"  Accuracy:  {df_trad['accuracy'].mean():.3f} ± {df_trad['accuracy'].std():.3f}")
        print(f"  Precision: {df_trad['precision'].mean():.3f} ± {df_trad['precision'].std():.3f}")
        print(f"  Recall:    {df_trad['recall'].mean():.3f} ± {df_trad['recall'].std():.3f}")
        print(f"  F1-Score:  {df_trad['f1'].mean():.3f} ± {df_trad['f1'].std():.3f}")
        
        print(f"\nRandom Forest Adaptativo:")
        print(f"  Accuracy:  {df_adapt['accuracy'].mean():.3f} ± {df_adapt['accuracy'].std():.3f}")
        print(f"  Precision: {df_adapt['precision'].mean():.3f} ± {df_adapt['precision'].std():.3f}")
        print(f"  Recall:    {df_adapt['recall'].mean():.3f} ± {df_adapt['recall'].std():.3f}")
        print(f"  F1-Score:  {df_adapt['f1'].mean():.3f} ± {df_adapt['f1'].std():.3f}")
        
        # Tendências ao longo do tempo
        print(f"\n📈 TENDÊNCIAS AO LONGO DO TEMPO:")
        print(f"F1-Score por Janela:")
        for i in range(len(df_trad)):
            janela = df_trad.iloc[i]['janela']
            f1_trad = df_trad.iloc[i]['f1']
            f1_adapt = df_adapt.iloc[i]['f1']
            
            if f1_adapt > f1_trad:
                melhor = "🔄"
            elif f1_trad > f1_adapt:
                melhor = "🏛️"
            else:
                melhor = "🤝"
            
            print(f"  Janela {janela}: Trad={f1_trad:.3f} | Adapt={f1_adapt:.3f} {melhor}")
        
        # Contagem de vitórias
        vitorias_trad = sum(1 for i in range(len(df_trad)) if df_trad.iloc[i]['f1'] > df_adapt.iloc[i]['f1'])
        vitorias_adapt = sum(1 for i in range(len(df_adapt)) if df_adapt.iloc[i]['f1'] > df_trad.iloc[i]['f1'])
        empates = len(df_trad) - vitorias_trad - vitorias_adapt
        
        print(f"\n🏆 RESULTADO FINAL:")
        print(f"  Vitórias Tradicional: {vitorias_trad}")
        print(f"  Vitórias Adaptativo: {vitorias_adapt}")
        print(f"  Empates: {empates}")
        
        if vitorias_adapt > vitorias_trad:
            print(f"  🏆 VENCEDOR: Random Forest Adaptativo")
        elif vitorias_trad > vitorias_adapt:
            print(f"  🏆 VENCEDOR: Random Forest Tradicional")
        else:
            print(f"  🤝 RESULTADO: Empate técnico")
        
        # Salvar resultados
        self._salvar_resultados(df_trad, df_adapt)
    
    def _salvar_resultados(self, df_trad, df_adapt):
        """Salva resultados em CSV para todos os cenários."""
        df_trad_inf = pd.DataFrame(self.historico_metricas['tradicional_infracoes'])
        df_adapt_inf = pd.DataFrame(self.historico_metricas['adaptativo_infracoes'])
        df_comparacao = pd.concat([df_trad, df_trad_inf, df_adapt, df_adapt_inf], ignore_index=True)
        df_comparacao.to_csv('comparacao_modelos_resultados.csv', index=False)
        print(f"\n💾 Resultados salvos em: comparacao_modelos_resultados.csv (todos os cenários)")
