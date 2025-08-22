"""
Comparador de Random Forest Tradicional vs. Adaptativo
======================================================

Compara o desempenho de modelos Random Forest em dados com mudanças temporais.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    f1_score, accuracy_score, average_precision_score, brier_score_loss,
    precision_score, recall_score,
)
from sklearn.ensemble import RandomForestClassifier

from haversine import haversine
from river import ensemble, tree, forest
from joblib import Parallel, delayed
from utils import processar_placa_basico

# Usando River para Random Forest Adaptativo real
class AdaptiveRandomForestWrapper:
    """Wrapper para o Random Forest Adaptativo do River com SMOTE incremental."""

    def __init__(
        self,
        n_models: int = 10,
        seed: int = 42,
        use_smote: bool = True,
        smote_k_neighbors: int = 3,
        ratio_threshold: float = 2.0,
        tag: str = "Adapt",
        verbose: bool = True,
    ) -> None:
        # Usar ARFClassifier (Adaptive Random Forest) do módulo forest
        self.arf = forest.ARFClassifier(
            n_models=n_models,
            seed=seed,
            leaf_prediction="nba",  # Naive Bayes Adaptive
            nominal_attributes=None,
        )
        # Configurações de balanceamento/SMOTE
        self.use_smote = use_smote
        self.smote_k_neighbors = smote_k_neighbors
        self.ratio_threshold = ratio_threshold
        self.tag = tag
        self.verbose = verbose
        # Estado interno
        self.class_counts = {0: 0, 1: 0}
        # Buffers separados por dimensionalidade das features para evitar mistura 3 vs 7
        # Estrutura: { n_features: { 'X': [ndarray], 'y': [ndarray] } }
        self.recent_samples = {}
        self.max_buffer_size = 1000  # Buffer para SMOTE
        self.initialized = False
        # RNG local para operações determinísticas
        self.seed = seed
        self._rng = np.random.RandomState(seed)
        
    def learn_batch(self, X, y, tag: str | None = None):
        """Aprende com um lote de dados aplicando SMOTE se necessário."""
        if len(X) == 0:
            return
        
        # Atualizar contadores de classe
        for label in y:
            self.class_counts[int(label)] += 1
        
        # Aplicar SMOTE se habilitado e houver desbalanceamento
        if self.use_smote and self._needs_balancing(y):
            X_balanced, y_balanced = self._apply_smote(X, y, tag=tag)
        else:
            X_balanced, y_balanced = X, y
        
        # Treinar incrementalmente
        for i in range(len(X_balanced)):
            x_dict = {f'feature_{j}': float(X_balanced[i][j]) for j in range(len(X_balanced[i]))}
            self.arf.learn_one(x_dict, int(y_balanced[i]))
        
        # Atualizar buffer de amostras recentes
        self._update_buffer(X, y)
        self.initialized = True
    
    def _needs_balancing(self, y):
        """Verifica se o batch atual precisa de balanceamento."""
        unique, counts = np.unique(y, return_counts=True)
        if len(unique) < 2:
            return False
        # Se a razão entre classes for muito desbalanceada
        ratio = max(counts) / min(counts)
        return ratio > float(self.ratio_threshold)  # Configurável via config
    
    def _apply_smote(self, X, y, tag: str | None = None):
        """Aplica SMOTE incremental usando buffer de amostras recentes."""
        try:
            from imblearn.over_sampling import SMOTE
            
            # Combinar dados atuais com buffer compatível (mesma dimensionalidade)
            n_features = X.shape[1] if len(X.shape) == 2 else len(X[0])
            bucket = self.recent_samples.get(n_features, {'X': [], 'y': []})
            if len(bucket['X']) > 0:
                X_combined = np.vstack([X] + bucket['X'])
                y_combined = np.hstack([y] + bucket['y'])
            else:
                X_combined, y_combined = X, y
            
            # Verificar se há amostras suficientes para SMOTE
            unique, counts = np.unique(y_combined, return_counts=True)
            min_samples_needed = min(self.smote_k_neighbors + 1, 6)
            
            if len(unique) >= 2 and all(counts >= min_samples_needed):
                smote = SMOTE(
                    k_neighbors=min(self.smote_k_neighbors, min(counts) - 1),
                    random_state=self.seed
                )
                X_balanced, y_balanced = smote.fit_resample(X_combined, y_combined)
                if self.verbose:
                    tag_str = f"[{tag}] " if tag else f"[{self.tag}] "
                    print(f"  🔄 {tag_str}SMOTE aplicado: {len(X)} → {len(X_balanced)} amostras")
                return X_balanced, y_balanced
            else:
                # Fallback: oversampling simples
                return self._simple_oversample(X, y)
                
        except Exception as e:
            if self.verbose:
                tag_str = f"[{tag}] " if tag else f"[{self.tag}] "
                print(f"  ⚠️ {tag_str}SMOTE falhou ({e}), usando oversampling simples")
            return self._simple_oversample(X, y)
    
    def _simple_oversample(self, X, y):
        """Oversampling simples como fallback."""
        unique, counts = np.unique(y, return_counts=True)
        if len(unique) < 2:
            return X, y
        
        # Encontrar classe minoritária
        min_class_idx = np.argmin(counts)
        min_class = unique[min_class_idx]
        max_count = np.max(counts)
        
        X_balanced = list(X)
        y_balanced = list(y)
        
        # Replicar amostras da classe minoritária
        minority_indices = np.where(y == min_class)[0]
        needed_samples = max_count - len(minority_indices)
        
        if needed_samples > 0:
            replicate_indices = self._rng.choice(minority_indices, needed_samples, replace=True)
            for idx in replicate_indices:
                X_balanced.append(X[idx])
                y_balanced.append(y[idx])
        
        return np.array(X_balanced), np.array(y_balanced)
    
    def _update_buffer(self, X, y):
        """Atualiza buffer de amostras recentes para SMOTE, separado por n_features."""
        n_features = X.shape[1] if len(X.shape) == 2 else len(X[0])
        if n_features not in self.recent_samples:
            self.recent_samples[n_features] = {'X': [], 'y': []}
        self.recent_samples[n_features]['X'].append(X.copy())
        self.recent_samples[n_features]['y'].append(y.copy())

        # Manter apenas as últimas 5 janelas por bucket
        if len(self.recent_samples[n_features]['X']) > 5:
            self.recent_samples[n_features]['X'].pop(0)
            self.recent_samples[n_features]['y'].pop(0)
    
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

    def predict_proba_batch(self, X):
        """Retorna probabilidades da classe positiva para um lote de dados."""
        if not self.initialized or len(X) == 0:
            return np.zeros(len(X))
        probs = []
        for i in range(len(X)):
            x_dict = {f'feature_{j}': float(X[i][j]) for j in range(len(X[i]))}
            try:
                proba = self.arf.predict_proba_one(x_dict)  # dict {classe: prob}
                p1 = float(proba.get(1, 0.0)) if isinstance(proba, dict) else 0.0
            except:
                p1 = 0.0
            probs.append(p1)
        return np.array(probs)

class ComparadorModelos:
    def __init__(self, simulador_streaming, n_jobs=8, config=None):
        self.simulador = simulador_streaming
        self.n_jobs = n_jobs
        self.config = config
        self.modelo_tradicional = None
        self.modelo_tradicional_multimodal = None

        # Configurações SMOTE (com compatibilidade retroativa)
        use_smote_global = self.config.get("usar_smote_adaptativo", True) if self.config else True
        use_smote_basico = self.config.get("usar_smote_adaptativo_basico", use_smote_global) if self.config else use_smote_global
        use_smote_mm = self.config.get("usar_smote_adaptativo_multimodal", use_smote_global) if self.config else use_smote_global

        smote_k = self.config.get("smote_k_neighbors", 3) if self.config else 3
        ratio_threshold = self.config.get("smote_ratio_threshold", 2.0) if self.config else 2.0

        seed_cfg = self.config.get("seed", 42) if self.config else 42
        self.modelo_adaptativo = AdaptiveRandomForestWrapper(
            n_models=10,
            seed=seed_cfg,
            use_smote=use_smote_basico,
            smote_k_neighbors=smote_k,
            ratio_threshold=ratio_threshold,
            tag="Basico"
        )
        self.modelo_adaptativo_multimodal = AdaptiveRandomForestWrapper(
            n_models=10,
            seed=seed_cfg,
            use_smote=use_smote_mm,
            smote_k_neighbors=smote_k,
            ratio_threshold=ratio_threshold,
            tag="Multimodal"
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
            seed = self.config.get("seed", 42)
            rf_n = self.config.get("rf_n_estimators", 100)
            rf_mf = self.config.get("rf_max_features", "sqrt")
            rf_md = self.config.get("rf_max_depth", None)

            self.modelo_tradicional_multimodal = RandomForestClassifier(
                n_estimators=rf_n, max_depth=rf_md, max_features=rf_mf,
                class_weight="balanced", n_jobs=self.n_jobs, random_state=seed
            )
            self.modelo_tradicional_multimodal.fit(X_treino, y_treino)
            print(f"✅ Modelo tradicional multimodal treinado com {len(X_treino):,} amostras")
        else:
            print("🌳 Treinando Random Forest Tradicional...")
            seed = self.config.get("seed", 42)
            rf_n = self.config.get("rf_n_estimators", 100)
            rf_mf = self.config.get("rf_max_features", "sqrt")
            rf_md = self.config.get("rf_max_depth", None)

            self.modelo_tradicional = RandomForestClassifier(
                n_estimators=rf_n, max_depth=rf_md, max_features=rf_mf,
                class_weight="balanced", n_jobs=self.n_jobs, random_state=seed
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
            if multimodal:
                self.modelo_adaptativo_multimodal.learn_batch(features, labels, tag="Multimodal")
            else:
                self.modelo_adaptativo.learn_batch(features, labels, tag="Basico")

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
                trad_metricas = self._avaliar_tradicional(X_input, y_teste, janela_numero, multimodal=multimodal)
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
            # Probabilidades (classe positiva = 1)
            try:
                proba = self.modelo_tradicional_multimodal.predict_proba(X_teste)
                # Garantir índice da classe 1
                classes = list(getattr(self.modelo_tradicional_multimodal, 'classes_', [0, 1]))
                pos_idx = classes.index(1) if 1 in classes else (proba.shape[1] - 1)
                y_score = proba[:, pos_idx]
            except Exception:
                y_score = np.zeros(len(y_teste))
            tipo = 'tradicional_multimodal'
        else:
            if self.modelo_tradicional is None:
                raise ValueError("Modelo tradicional não foi treinado")
            y_pred = self.modelo_tradicional.predict(X_teste)
            try:
                proba = self.modelo_tradicional.predict_proba(X_teste)
                classes = list(getattr(self.modelo_tradicional, 'classes_', [0, 1]))
                pos_idx = classes.index(1) if 1 in classes else (proba.shape[1] - 1)
                y_score = proba[:, pos_idx]
            except Exception:
                y_score = np.zeros(len(y_teste))
            tipo = 'tradicional'
        # Métricas complementares por janela
        try:
            auprc = average_precision_score(y_teste, y_score) if len(np.unique(y_teste)) > 1 else np.nan
        except Exception:
            auprc = np.nan
        try:
            brier = brier_score_loss(y_teste, y_score)
        except Exception:
            brier = np.nan
        return {
            'janela': janela_numero,
            'accuracy': accuracy_score(y_teste, y_pred),
            'precision': precision_score(y_teste, y_pred, zero_division=0),
            'recall': recall_score(y_teste, y_pred, zero_division=0),
            'f1': f1_score(y_teste, y_pred, zero_division=0),
            'auprc': auprc,
            'brier': brier,
            'n_amostras': len(y_teste),
            'n_suspeitos': sum(y_teste),
            'tipo': tipo,
            'y_true': json.dumps([int(v) for v in y_teste.tolist()]),
            'y_score': json.dumps([float(v) for v in y_score.tolist()])
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
        if multimodal:
            y_pred = self.modelo_adaptativo_multimodal.predict_batch(X_teste)
            y_score = self.modelo_adaptativo_multimodal.predict_proba_batch(X_teste)
        else:
            y_pred = self.modelo_adaptativo.predict_batch(X_teste)
            y_score = self.modelo_adaptativo.predict_proba_batch(X_teste)
        if multimodal:
            tipo = 'adaptativo_multimodal'
        else:
            tipo = 'adaptativo'
        # Métricas complementares por janela
        try:
            auprc = average_precision_score(y_teste, y_score) if len(np.unique(y_teste)) > 1 else np.nan
        except Exception:
            auprc = np.nan
        try:
            brier = brier_score_loss(y_teste, y_score)
        except Exception:
            brier = np.nan
        return {
            'janela': janela_numero,
            'accuracy': accuracy_score(y_teste, y_pred),
            'precision': precision_score(y_teste, y_pred, zero_division=0),
            'recall': recall_score(y_teste, y_pred, zero_division=0),
            'f1': f1_score(y_teste, y_pred, zero_division=0),
            'auprc': auprc,
            'brier': brier,
            'n_amostras': len(y_teste),
            'n_suspeitos': sum(y_teste),
            'tipo': tipo,
            'y_true': json.dumps([int(v) for v in y_teste.tolist()]),
            'y_score': json.dumps([float(v) for v in y_score.tolist()])
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
            # Ainda assim salvar um CSV vazio com cabeçalho para não quebrar a análise posterior
            print("❌ Nenhuma métrica disponível para análise — salvando CSV vazio com cabeçalho")
            try:
                self._salvar_resultados(pd.DataFrame(), pd.DataFrame())
            except Exception as _e:
                # Não bloquear fluxo por erro ao salvar vazio
                pass
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

        # Garantir esquema consistente: incluir colunas complementares, mesmo que ausentes
        colunas_complementares = ['auprc', 'brier', 'y_true', 'y_score']
        for df in (df_trad, df_trad_mm, df_adapt, df_adapt_mm):
            if df is not None and not df.empty:
                for col in colunas_complementares:
                    if col not in df.columns:
                        # y_* como strings vazias; métricas como NaN
                        df[col] = '' if col.startswith('y_') else np.nan

        # Avisos se colunas complementares estiverem ausentes antes do concat
        for nome, d in [("tradicional", df_trad), ("tradicional_multimodal", df_trad_mm),
                        ("adaptativo", df_adapt), ("adaptativo_multimodal", df_adapt_mm)]:
            try:
                if d is not None and not d.empty:
                    faltando = [c for c in colunas_complementares if c not in d.columns]
                    if faltando:
                        print(f"⚠️  DataFrame {nome} sem colunas: {faltando}")
            except Exception:
                pass

        # Concatenação segura (mesmo que todos estejam vazios)
        frames = [df_trad, df_trad_mm, df_adapt, df_adapt_mm]
        # Garante que existam DataFrames, mesmo que vazios
        frames = [f if isinstance(f, pd.DataFrame) else pd.DataFrame() for f in frames]
        df_comparacao = pd.concat(frames, ignore_index=True)

        # Debug: imprimir colunas salvas
        try:
            print(f"🧾 Colunas no CSV: {list(df_comparacao.columns)}")
        except Exception:
            pass
        
        # Usar pasta de CSVs configurável
        pasta_csvs = self.config.get("pasta_csvs", "csvs") if self.config else "csvs"
        
        # Criar pasta se não existir
        import os
        if not os.path.exists(pasta_csvs):
            os.makedirs(pasta_csvs)
            print(f"📁 Pasta CSV criada: {pasta_csvs}")

        # Ordenação determinística e ordem fixa de colunas antes de salvar
        try:
            df_comparacao = df_comparacao.sort_values(by=['janela', 'tipo'], kind='mergesort').reset_index(drop=True)
        except Exception:
            pass
        # Ordem de colunas estável (mantém as existentes e ignora ausentes)
        col_order = ['janela', 'accuracy', 'precision', 'recall', 'f1', 'auprc', 'brier',
                     'n_amostras', 'n_suspeitos', 'tipo', 'y_true', 'y_score',
                     'num_infracoes', 'semelhanca']
        if df_comparacao.empty:
            # Criar DataFrame vazio com cabeçalho padrão
            df_comparacao = pd.DataFrame(columns=col_order)
        else:
            cols_present = [c for c in col_order if c in df_comparacao.columns]
            others = [c for c in df_comparacao.columns if c not in cols_present]
            df_comparacao = df_comparacao[cols_present + others]

        # Salvar CSV na pasta configurada
        arquivo_csv = os.path.join(pasta_csvs, 'comparacao_modelos_resultados.csv')
        df_comparacao.to_csv(arquivo_csv, index=False)
        print(f"\n💾 Resultados salvos em: {arquivo_csv} (cenários básico e multimodal)")
        
# Funções auxiliares para avaliação e salvamento de resultados

def _metrics_row(janela_id, tipo, y_true, y_score, limiar=0.5, extras=None):
    """Gera linha padronizada com F1/Accuracy/AUCPR/Brier e serializa y_true/y_score."""
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)
    has_two_classes = np.unique(y_true).size > 1
    y_pred = (y_score >= limiar).astype(int) if y_score.size else np.array([], dtype=int)

    f1 = f1_score(y_true, y_pred) if has_two_classes and y_pred.size else np.nan
    acc = accuracy_score(y_true, y_pred) if y_pred.size else np.nan
    aucpr = average_precision_score(y_true, y_score) if has_two_classes and y_score.size else np.nan
    brier = brier_score_loss(y_true, y_score) if y_score.size else np.nan

    row = {
        "janela": int(janela_id),
        "tipo": str(tipo),  # tradicional | tradicional_multimodal | adaptativo | adaptativo_multimodal
        "F1": float(f1) if f1==f1 else np.nan,
        "Accuracy": float(acc) if acc==acc else np.nan,
        "AUCPR": float(aucpr) if aucpr==aucpr else np.nan,
        "Brier": float(brier) if brier==brier else np.nan,
        "y_true": json.dumps([int(v) for v in y_true.tolist()]),
        "y_score": json.dumps([float(v) for v in y_score.tolist()]),
    }
    if extras:
        row.update(extras)
    return row

# ========= Exemplo de uso no batch (Trad e Trad+Multi) =========
def _avaliar_batch(modelo, X_test, y_test, janela_id, tipo, limiar):
    """Avalia um RandomForest batch e retorna linha de métricas incluindo probabilidades."""
    # Requer que modelo tenha predict_proba
    y_score = modelo.predict_proba(X_test)[:, 1]
    return _metrics_row(janela_id, tipo, y_test, y_score, limiar=limiar)

# ========= Exemplo de uso no adaptativo (ARF) =========
def _avaliar_adaptativo(arf_model, X_window, y_window, janela_id, tipo, limiar):
    """Avalia ARF em modo test-then-train: coleta probas antes do treino da janela."""
    y_true_list, y_score_list = [], []
    for xi, yi in zip(X_window, y_window):
        # xi deve ser dict-like se usar river; ajuste conforme seu wrapper
        proba = arf_model.predict_proba_one(xi).get(1, 0.0)
        y_true_list.append(int(yi))
        y_score_list.append(float(proba))
    return _metrics_row(janela_id, tipo, y_true_list, y_score_list, limiar=limiar)

# ========= Ao final, salve no CSV do cenário =========
def _salvar_resultados(rows: list, config: dict):
    df = pd.DataFrame(rows)
    # Ordem de colunas estável
    col_order = ["janela","tipo","F1","Accuracy","AUCPR","Brier","y_true","y_score"]
    for c in col_order:
        if c not in df.columns:
            df[c] = np.nan
    df = df[col_order].sort_values(["janela","tipo"]).reset_index(drop=True)

    pasta_csvs = Path(config.get("pasta_csvs", "csvs"))
    pasta_csvs.mkdir(parents=True, exist_ok=True)
    out_csv = pasta_csvs / "comparacao_modelos_resultados.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"💾 Resultados salvos em: {out_csv} — colunas: {list(df.columns)}")
