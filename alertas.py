"""
Módulo de Geração de Alertas JSON-LD
=====================================

Sistema simplificado para protótipo de geração de alertas padronizados
conforme especificação da tese de doutorado.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class GeradorAlertasSimples:
    """
    Gerador de alertas JSON-LD (protótipo) para validação do modelo.
    - Sem dependências externas.
    - Estrutura compatível com o exemplo da tese.
    - Inclui classificação simples por score.
    """
    
    def __init__(self,
                 identificador_sistema: str = "MOPRED-SC-01",
                 contexto_url: str = "https://www.mopred.org/schemas/alerta/v1",
                 limiar_alerta: float = 0.80,
                 status_padrao: str = "Real",
                 escopo_padrao: str = "Restrito"):
        self.identificador_sistema = identificador_sistema
        self.contexto_url = contexto_url
        self.limiar_alerta = limiar_alerta
        self.status_padrao = status_padrao
        self.escopo_padrao = escopo_padrao

    @staticmethod
    def _uuid_urn() -> str:
        """Gera URN UUID único para o alerta."""
        return f"urn:uuid:{uuid.uuid4()}"

    @staticmethod
    def _agora_utc_iso() -> str:
        """Retorna timestamp atual em formato ISO8601 UTC com sufixo Z."""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _classificar_por_score(score: float) -> Dict[str, str]:
        """
        Classifica severidade, urgência e certeza baseado no score.
        Regras simples para protótipo; ajuste conforme sua política.
        """
        if score >= 0.90:
            return {"severidade": "Alta", "urgencia": "Imediata", "certeza": "Provável"}
        elif score >= 0.80:
            return {"severidade": "Média", "urgencia": "Próxima", "certeza": "Possível"}
        else:
            return {"severidade": "Baixa", "urgencia": "Rotina", "certeza": "Indeterminado"}

    def criar_alerta(self,
                     passagem: Dict[str, Any],
                     explicabilidade: Optional[Dict[str, Any]] = None,
                     recursos: Optional[List[Dict[str, Any]]] = None,
                     status: Optional[str] = None,
                     escopo: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria alerta JSON-LD baseado nos dados da passagem e explicabilidade.
        
        Args:
            passagem: Dados da passagem com chaves mínimas:
                - placa: Placa do veículo
                - escore: Score de suspeição (0.0-1.0)
                - timestampDeteccao: Timestamp da detecção
                - lat, lon: Coordenadas geográficas
                - descricaoArea: Descrição da localização
                - modeloInferido: Modelo/cor do veículo inferido
            explicabilidade: Dados da explicabilidade SHAP (opcional)
            recursos: Lista de recursos adicionais (opcional)
            status: Status do alerta (padrão: "Real")
            escopo: Escopo do alerta (padrão: "Restrito")
        
        Returns:
            Dict com alerta no formato JSON-LD
        """
        score = float(passagem.get("escore", 0.0))
        cls = self._classificar_por_score(score)

        # Parametrização preditiva mínima
        params = [
            {"nome": "placaVeiculo", "valor": str(passagem.get("placa", ""))},
            {"nome": "escoreSuspeicao", "valor": f"{score:.2f}", "metrica": "Probabilidade"},
            {"nome": "modeloVeiculoInferido", "valor": str(passagem.get("modeloInferido", ""))}
        ]

        # Montar recursos (anexa explicabilidade como "Contexto da Inferência", se fornecida)
        recursos_final: List[Dict[str, Any]] = []
        if explicabilidade:
            recursos_final.append({
                "descricaoRecurso": "Contexto da Inferência",
                "mimeType": "application/json",
                "conteudo": explicabilidade
            })
        if recursos:
            recursos_final.extend(recursos)

        alerta = {
            "@context": self.contexto_url,
            "@type": "AlertaPreditivo",
            "id": self._uuid_urn(),
            "identificadorSistema": self.identificador_sistema,
            "timestampEmissao": self._agora_utc_iso(),
            "status": status or self.status_padrao,
            "escopo": escopo or self.escopo_padrao,

            "info": {
                "evento": "Comportamento Veicular Suspeito",
                "severidade": cls["severidade"],
                "urgencia": cls["urgencia"],
                "certeza": cls["certeza"],
                "descricao": f"Veículo com alta probabilidade de envolvimento em atividade ilícita (escore de suspeição: {score:.2f}).",
                "instrucao": "Abordagem prioritária da viatura policial mais próxima. Proceder com cautela.",
                "parametrosPreditivos": params
            },

            "area": {
                "descricaoArea": str(passagem.get("descricaoArea", "")),
                "geometria": {
                    "@type": "Ponto",  # Mantido conforme exemplo da tese
                    "coordenadas": [float(passagem.get("lat", 0.0)), float(passagem.get("lon", 0.0))]
                }
            },

            "recursos": recursos_final
        }
        return alerta

    @staticmethod
    def to_json(alerta: Dict[str, Any], indent: Optional[int] = None) -> str:
        """Converte alerta para string JSON formatada."""
        if indent is None or indent == 0:
            # Para NDJSON: sem quebras de linha, compacto
            return json.dumps(alerta, ensure_ascii=False, separators=(",", ":"))
        else:
            # Para visualização: com indentação
            return json.dumps(alerta, ensure_ascii=False, indent=indent)

    def deve_gerar_alerta(self, score: float) -> bool:
        """Verifica se deve gerar alerta baseado no score."""
        return score >= self.limiar_alerta

    def processar_batch_alertas(self, 
                               pares_info: List[Dict[str, Any]], 
                               scores: List[float],
                               explicabilidades: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Processa um lote de predições e gera alertas para casos suspeitos.
        
        Args:
            pares_info: Lista de metadados dos pares
            scores: Lista de scores de suspeição
            explicabilidades: Lista de explicabilidades SHAP (opcional)
        
        Returns:
            Lista de alertas gerados
        """
        alertas = []
        
        for i, (meta, score) in enumerate(zip(pares_info, scores)):
            if self.deve_gerar_alerta(float(score)):
                # Preparar dados da passagem
                passagem = {
                    "placa": meta.get("placa", meta.get("placa_pseudo", "")),
                    "escore": float(score),
                    "timestampDeteccao": meta.get("timestamp", ""),
                    "lat": meta.get("lat", 0.0),
                    "lon": meta.get("lon", 0.0),
                    "descricaoArea": meta.get("descricaoArea", ""),
                    "modeloInferido": meta.get("modeloInferido", "")
                }
                
                # Obter explicabilidade correspondente, se disponível
                explic = explicabilidades[i] if explicabilidades and i < len(explicabilidades) else None
                
                # Criar alerta
                alerta = self.criar_alerta(passagem, explicabilidade=explic)
                alertas.append(alerta)
        
        return alertas


def extrair_explicabilidade_shap(shap_values, feature_names, feature_values, modelo_id="RF-v2.1.3"):
    """
    Extrai explicabilidade SHAP para um caso específico.
    
    Args:
        shap_values: Valores SHAP para o caso
        feature_names: Nomes das features
        feature_values: Valores das features
        modelo_id: ID do modelo
    
    Returns:
        Dict com dados da explicabilidade
    """
    contribuicoes = []
    fatores_risco = []
    
    # Tradução de features para português
    traducao = {
        "dist_km": "Distância entre câmeras (km)",
        "delta_t_segundos": "Tempo entre leituras (segundos)",
        "velocidade_kmh": "Velocidade estimada (km/h)",
        "num_infracoes": "Número de infrações",
        "marca_modelo_igual": "Marca/modelo iguais",
        "tipo_igual": "Tipo igual",
        "cor_igual": "Cor igual"
    }
    
    for i, (feature, shap_val, feat_val) in enumerate(zip(feature_names, shap_values, feature_values)):
        if isinstance(shap_val, (list, tuple)) and len(shap_val) > 1:
            impacto = float(shap_val[1])  # Classe positiva
        elif hasattr(shap_val, '__len__') and len(shap_val) > 1:
            impacto = float(shap_val[1])  # Classe positiva
        elif hasattr(shap_val, '__len__') and len(shap_val) == 1:
            impacto = float(shap_val[0])
        elif hasattr(shap_val, 'item'):
            impacto = float(shap_val.item())
        else:
            impacto = float(shap_val)
        
        contribuicoes.append({
            "feature": traducao.get(feature, feature),
            "valor": float(feat_val),
            "impacto": impacto,
            "sinal": "+" if impacto >= 0 else "-"
        })
        
        # Gerar fatores de risco baseados em impacto alto
        if abs(impacto) > 0.1:  # Threshold para considerar relevante
            if feature == "velocidade_kmh" and feat_val > 120:
                fatores_risco.append("Velocidade incompatível com o fluxo da via.")
            elif feature == "num_infracoes" and feat_val > 5:
                fatores_risco.append("Histórico elevado de infrações.")
            elif feature in ["marca_modelo_igual", "tipo_igual", "cor_igual"] and feat_val == 1:
                fatores_risco.append("Alta similaridade visual com outro veículo.")
            elif feature == "dist_km" and feat_val > 50:
                fatores_risco.append("Rota incomum para o dia/horário.")
    
    explicabilidade = {
        "idModelo": modelo_id,
        "metodo": "SHAP",
        "contribuicoes": contribuicoes,
        "fatoresDeRisco": fatores_risco if fatores_risco else ["Padrão de comportamento atípico detectado."]
    }
    
    return explicabilidade
