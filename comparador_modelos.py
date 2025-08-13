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
from joblib import Parallel, delayed
from utils import processar_placa_basico

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
    def __init__(self, simulador_streaming, n_jobs=8, config=None):
        self.simulador = simulador_streaming
        self.n_jobs = n_jobs
        self.config = config  # Armazenar configuração
        self.modelo_tradicional = None
        self.modelo_tradicional_multimodal = None
        self.modelo_adaptativo = AdaptiveRandomForestWrapper(
            n_models=10,
            seed=42
        )
        self.historico_metricas = {
            'tradicional': [],
            'tradicional_multimodal': [],
            'adaptativo': [],
            'adaptativo_multimodal': []
        }
        
    def treinar_modelo_tradicional(self, X_treino, y_treino, multimodal=False):
        """Treina o modelo Random Forest tradicional (básico ou multimodal)."""
        if multimodal:
            print("🌳 Treinando Random Forest Tradicional (multimodal: infrações + semelhança visual)...")
            self.modelo_tradicional_multimodal = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced',
                n_jobs=self.n_jobs
            )
            self.modelo_tradicional_multimodal.fit(X_treino, y_treino)
            print(f"✅ Modelo tradicional multimodal treinado com {len(X_treino):,} amostras")
        else:
            print("🌳 Treinando Random Forest Tradicional...")
            self.modelo_tradicional = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=self.n_jobs
            )
            self.modelo_tradicional.fit(X_treino, y_treino)
            print(f"✅ Modelo tradicional treinado com {len(X_treino):,} amostras")
    
    def processar_janela_adaptativo(self, eventos_janela, multimodal=False):
        """
        Processa uma janela de eventos para o modelo adaptativo.
        
        Args:
            eventos_janela: Lista de eventos para processamento
            multimodal: Se True, usa o modelo multimodal (infrações + semelhança); se False, usa o modelo básico
        """
        if multimodal:
            features, labels, _ = self._gerar_features_janela_multimodal(eventos_janela)
        else:
            features, labels, _ = self._gerar_features_janela(eventos_janela)

        if len(features) > 0:
            self.modelo_adaptativo.learn_batch(features, labels)

        return features, labels
    
    def avaliar_janela(self, eventos_janela, janela_numero, multimodal=False):
        """
        Avalia ambos os modelos em uma janela de teste.
        
        Args:
            eventos_janela: Lista de eventos para avaliação
            janela_numero: Identificador da janela
            multimodal: Se True, usa o modelo multimodal (infrações + semelhança); se False, usa o modelo básico
        """
        print(f"\n📊 Avaliando Janela {janela_numero} ({len(eventos_janela)} eventos)" + (" [multimodal]" if multimodal else " [básico]"))

        # Gerar features para teste
        if multimodal:
            X_teste, y_teste, pares_info = self._gerar_features_janela_multimodal(eventos_janela)
        else:
            X_teste, y_teste, pares_info = self._gerar_features_janela(eventos_janela)

        # Se não houver dados suficientes, retorna métricas nulas
        if len(X_teste) == 0 or len(y_teste) == 0:
            print(f"⚠️ Janela {janela_numero} sem dados suficientes para avaliação.")
            return (
                {'janela': janela_numero, 'accuracy': None, 'precision': None, 'recall': None, 'f1': None, 'n_amostras': 0, 'n_suspeitos': 0, 'tipo': 'tradicional_multimodal' if multimodal else 'tradicional'},
                {'janela': janela_numero, 'accuracy': None, 'precision': None, 'recall': None, 'f1': None, 'n_amostras': 0, 'n_suspeitos': 0, 'tipo': 'adaptativo_multimodal' if multimodal else 'adaptativo'}
            )

        # Configurar modelo e tipo com base no parâmetro multimodal
        if multimodal:
            tipo = 'tradicional_multimodal'
            modelo = getattr(self, 'modelo_tradicional_multimodal', None)
            X_input = X_teste  # 7 features from _gerar_features_janela_multimodal
        else:
            tipo = 'tradicional'
            modelo = getattr(self, 'modelo_tradicional', None)
            X_input = X_teste  # Usa as features básicas
        
        if modelo is not None:
            try:
                y_pred = modelo.predict(X_input)
                trad_metricas = {
                    'janela': janela_numero,
                    'accuracy': accuracy_score(y_teste, y_pred),
                    'precision': precision_score(y_teste, y_pred, zero_division=0),
                    'recall': recall_score(y_teste, y_pred, zero_division=0),
                    'f1': f1_score(y_teste, y_pred, zero_division=0),
                    'n_amostras': len(y_teste),
                    'n_suspeitos': sum(y_teste),
                    'tipo': tipo
                }
            except ValueError as e:
                print(f"❌ Erro ao avaliar modelo '{tipo}': {e}")
                trad_metricas = {'janela': janela_numero, 'accuracy': None, 'precision': None, 'recall': None, 'f1': None, 'n_amostras': len(y_teste), 'n_suspeitos': sum(y_teste), 'tipo': tipo}
        else:
            print(f"❌ Modelo '{tipo}' não treinado ou não encontrado para avaliação.")
            trad_metricas = {'janela': janela_numero, 'accuracy': None, 'precision': None, 'recall': None, 'f1': None, 'n_amostras': len(y_teste), 'n_suspeitos': sum(y_teste), 'tipo': tipo}

        # Avaliação adaptativa
        adapt_tipo = 'adaptativo_multimodal' if multimodal else 'adaptativo'
        # Avaliar modelo adaptativo
        adapt_metricas = self._avaliar_adaptativo(X_teste, y_teste, janela_numero, multimodal=multimodal)
        
        # Salvar métricas no histórico
        if multimodal:
            self.historico_metricas['tradicional_multimodal'].append(trad_metricas)
            self.historico_metricas['adaptativo_multimodal'].append(adapt_metricas)
            # Registrar médias das features multimodais para exportação
            if not hasattr(self, 'janela_features_multimodal'):
                self.janela_features_multimodal = {}
            # Calcular médias das features na janela
            if X_teste.shape[1] >= 5:
                media_infracoes = float(np.mean(X_teste[:, 3]))
                media_semelhanca = float(np.mean(X_teste[:, 4]))
            else:
                media_infracoes = None
                media_semelhanca = None
            self.janela_features_multimodal[(janela_numero, 'tradicional_multimodal')] = {
                'num_infracoes': media_infracoes,
                'semelhanca': media_semelhanca
            }
            self.janela_features_multimodal[(janela_numero, 'adaptativo_multimodal')] = {
                'num_infracoes': media_infracoes,
                'semelhanca': media_semelhanca
            }
        else:
            self.historico_metricas['tradicional'].append(trad_metricas)
            self.historico_metricas['adaptativo'].append(adapt_metricas)
        return trad_metricas, adapt_metricas
    
    def _gerar_features_janela_multimodal(self, eventos_janela):
        """Gera features para uma janela de eventos, incluindo num_infracoes e features de semelhança visual."""
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
                
                # Decompor semelhança em 3 features booleanas
                marca_modelo_igual = 1.0 if (evento1.get('marca') == evento2.get('marca') and 
                                             evento1.get('modelo') == evento2.get('modelo')) else 0.0
                tipo_igual = 1.0 if evento1.get('tipo') == evento2.get('tipo') else 0.0
                cor_igual = 1.0 if evento1.get('cor') == evento2.get('cor') else 0.0
                
                feature_vector = [dist_km, delta_t_segundos, velocidade_kmh, num_infracoes, 
                                marca_modelo_igual, tipo_igual, cor_igual]
                features.append(feature_vector)
                is_suspeito = velocidade_kmh > 150 or evento1.get('is_clonado', False)
                labels.append(1 if is_suspeito else 0)
                par_info = {
                    'placa': placa,
                    'dist_km': dist_km,
                    'delta_t_segundos': delta_t_segundos,
                    'velocidade_kmh': velocidade_kmh,
                    'num_infracoes': num_infracoes,
                    'marca_modelo_igual': marca_modelo_igual,
                    'tipo_igual': tipo_igual,
                    'cor_igual': cor_igual,
                    'is_clonado': evento1.get('is_clonado', False)
                }
                pares_info.append(par_info)
        return np.array(features), np.array(labels), pares_info

    def _avaliar_tradicional(self, X_teste, y_teste, janela_numero, multimodal=False):
        """Avalia o modelo tradicional (sem retreinamento). Se multimodal=True, usa o modelo multimodal."""
        if multimodal:
            if self.modelo_tradicional_multimodal is None:
                raise ValueError("Modelo tradicional multimodal não foi treinado")
            y_pred = self.modelo_tradicional_multimodal.predict(X_teste)
            tipo = 'tradicional_multimodal'
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
    
    def _avaliar_adaptativo(self, X_teste, y_teste, janela_numero, multimodal=False):
        """
        Avalia o modelo adaptativo.
        
        Args:
            X_teste: Features para avaliação
            y_teste: Labels para avaliação
            janela_numero: Identificador da janela
            multimodal: Se True, usa o modelo multimodal (infrações + semelhança); se False, usa o modelo básico
            
        Returns:
            Dict com métricas de avaliação
        """
        y_pred = self.modelo_adaptativo.predict_batch(X_teste)
        if multimodal:
            tipo = 'adaptativo_multimodal'
        else:
            tipo = 'adaptativo'
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
        
        resultados = Parallel(n_jobs=self.n_jobs, backend="multiprocessing")(
            delayed(processar_placa_basico)(df_janela[df_janela['placa'] == placa].sort_values('ts'))
            for placa in placas_unicas
        )
        features, labels, pares_info = [], [], []
        for f, l, p in resultados:
            features.extend(f)
            labels.extend(l)
            pares_info.extend(p)
        
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
        df_trad_mm = pd.DataFrame(self.historico_metricas['tradicional_multimodal'])
        df_adapt_mm = pd.DataFrame(self.historico_metricas['adaptativo_multimodal'])

        # Adiciona médias das features multimodais por janela
        def add_multimodal_features(df_mm, tipo):
            if df_mm.empty:
                return df_mm
            # Para cada janela, calcular média das features
            if 'janela' in df_mm.columns and hasattr(self, 'janela_features_multimodal'):
                medias = []
                for janela in df_mm['janela']:
                    feats = self.janela_features_multimodal.get((janela, tipo), None)
                    if feats:
                        medias.append({'num_infracoes': feats.get('num_infracoes', None), 'semelhanca': feats.get('semelhanca', None)})
                    else:
                        medias.append({'num_infracoes': None, 'semelhanca': None})
                df_mm = df_mm.copy()
                df_mm['num_infracoes'] = [m['num_infracoes'] for m in medias]
                df_mm['semelhanca'] = [m['semelhanca'] for m in medias]
            return df_mm

        df_trad_mm = add_multimodal_features(df_trad_mm, 'tradicional_multimodal')
        df_adapt_mm = add_multimodal_features(df_adapt_mm, 'adaptativo_multimodal')

        df_comparacao = pd.concat([df_trad, df_trad_mm, df_adapt, df_adapt_mm], ignore_index=True)
        
        # Usar pasta de CSVs configurável
        pasta_csvs = self.config.get("pasta_csvs", "csvs") if self.config else "csvs"
        
        # Criar pasta se não existir
        import os
        if not os.path.exists(pasta_csvs):
            os.makedirs(pasta_csvs)
            print(f"📁 Pasta CSV criada: {pasta_csvs}")
        
        # Salvar CSV na pasta configurada
        arquivo_csv = os.path.join(pasta_csvs, 'comparacao_modelos_resultados.csv')
        df_comparacao.to_csv(arquivo_csv, index=False)
        print(f"\n💾 Resultados salvos em: {arquivo_csv} (cenários básico e multimodal)")
