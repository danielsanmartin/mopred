"""
Simulador de Streaming ALPR
===========================

Simula um streaming de dados ALPR em tempo real, gerando passagens
em ordem cronológica para testar algoritmos adaptativos vs. tradicionais.

Autor: Sistema ALPR
Data: 2025
"""

import pandas as pd
import json
import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Generator
import os
import threading
import queue
from dataclasses import dataclass
from enum import Enum

class ModoSimulacao(Enum):
    """Modos de simulação disponíveis."""
    BATCH_COMPLETO = "batch_completo"
    STREAMING_TEMPO_REAL = "streaming_tempo_real"
    STREAMING_ACELERADO = "streaming_acelerado"
    JANELAS_TEMPORAIS = "janelas_temporais"

@dataclass
class EventoALPR:
    """Representa um evento de captura ALPR."""
    placa: str
    timestamp: int  # milissegundos
    cam: str
    faixa: int
    lat: float
    lon: float
    is_clonado: bool = False
    num_infracoes: int = 0
    semelhanca: float = 1.0
    marca: str = ""
    modelo: str = ""
    tipo: str = ""
    cor: str = ""

    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            'placa': self.placa,
            'timestamp': self.timestamp,
            'cam': self.cam,
            'faixa': self.faixa,
            'lat': self.lat,
            'lon': self.lon,
            'timestamp_legivel': pd.to_datetime(self.timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S'),
            'is_clonado': self.is_clonado,
            'num_infracoes': self.num_infracoes,
            'semelhanca': self.semelhanca,
            'marca': self.marca,
            'modelo': self.modelo,
            'tipo': self.tipo,
            'cor': self.cor
        }

class SimuladorStreamingALPR:
    def calcular_semelhanca_visual(self, is_clonado, idx, rota_len, percentual_clones_identicos):
        """
        Calcula a semelhança visual conforme regras do simulador:
        - Não clonados: próxima de 1.0 com ruído
        - Clonados idênticos: próxima de 1.0 com ruído
        - Clonados não idênticos: pelas 3 características principais + ruído
        """
        # Características simuladas (exemplo): tipo, cor, modelo
        tipo_igual = random.random() < 0.8  # 80% chance de tipo igual
        cor_igual = random.random() < 0.7   # 70% chance de cor igual
        modelo_igual = random.random() < 0.6 # 60% chance de modelo igual
        # Pesos ajustados para totalizar 1.0
        peso_tipo = 0.33
        peso_cor = 0.33
        peso_modelo = 0.34

        if is_clonado:
            if idx < int(percentual_clones_identicos * rota_len):
                # Clonado idêntico: semelhança próxima de 1.0 com ruído
                semelhanca = min(max(random.uniform(0.97, 1.0) + random.normalvariate(0, 0.01), 0), 1)
            else:
                # Clonado não idêntico: calcula pelas características + ruído
                semelhanca = 0
                semelhanca += peso_tipo if tipo_igual else 0
                semelhanca += peso_cor if cor_igual else 0
                semelhanca += peso_modelo if modelo_igual else 0
                semelhanca += random.normalvariate(0, 0.03)
                semelhanca = min(max(semelhanca, 0), 1)
        else:
            # Não clonado: semelhança próxima de 1.0 com ruído
            semelhanca = min(max(random.uniform(0.97, 1.0) + random.normalvariate(0, 0.01), 0), 1)
        return semelhanca
    def __init__(self, config_path: str = "config.json"):
        """
        Inicializa o simulador de streaming ALPR.
        
        Args:
            config_path (str): Caminho para o arquivo de configuração
        """
        self.config = self.carregar_config(config_path)
        self.sensores = []
        self.veiculos = pd.DataFrame()
        self.eventos_gerados = []
        self.streaming_ativo = False
        self.pausa_streaming = False
        
        print(f"🎬 Simulador Streaming ALPR inicializado")
        self._imprimir_config()
    
    def carregar_config(self, config_path: str) -> Dict:
        """Carrega o arquivo de configuração."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✅ Configuração carregada de {config_path}")
        return config
    
    def carregar_veiculos(self, csv_path: str = None) -> None:
        """Carrega os veículos do arquivo CSV."""
        if csv_path is None:
            csv_path = self.config.get("csv_veiculos_path", "veiculos_gerados.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Arquivo de veículos não encontrado: {csv_path}")
        
        self.veiculos = pd.read_csv(csv_path)
        print(f"✅ {len(self.veiculos):,} veículos carregados de {csv_path}")
        print(f"   🚗 Veículos normais: {len(self.veiculos[self.veiculos['clonado'] == 0]):,}")
        print(f"   ⚠️  Veículos clonados: {len(self.veiculos[self.veiculos['clonado'] == 1]):,}")
    
    def _imprimir_config(self) -> None:
        """Imprime as principais configurações carregadas."""
        print(f"📋 Configurações principais:")
        print(f"   ⏱️  Tempo de simulação: {self.config['intervalo_tempo_simulacao_horas']}h")
        print(f"   📡 Total de sensores: {self.config['n_sensores']}")
        print(f"   🏙️  Cidades: {len(self.config['sensores_por_cidade'])}")
        print(f"   📊 Passagens por veículo: {self.config['n_passagens_min']}-{self.config['n_passagens_max']}")
    
    def distribuir_sensores(self) -> None:
        """Distribui sensores pelas cidades conforme configuração."""
        print(f"📡 Distribuindo {self.config['n_sensores']} sensores...")
        
        self.sensores = []
        sensor_id = 1
        
        for cidade, quantidade in self.config['sensores_por_cidade'].items():
            if cidade not in self.config['lat_lon_por_cidade']:
                print(f"⚠️  Cidade {cidade} não encontrada nas coordenadas")
                continue
            
            lat_base, lon_base = self.config['lat_lon_por_cidade'][cidade]
            
            for i in range(quantidade):
                # Gera coordenadas com jitter
                lat, lon = self.gerar_coordenada_com_jitter(lat_base, lon_base)
                
                sensor = {
                    'cam': f"CAM{sensor_id:03d}",
                    'cidade': cidade,
                    'lat': round(lat, 6),
                    'lon': round(lon, 6),
                    'faixas': random.randint(1, 4)
                }
                
                self.sensores.append(sensor)
                sensor_id += 1
        
        print(f"✅ {len(self.sensores)} sensores distribuídos")
    
    def gerar_coordenada_com_jitter(self, lat_base: float, lon_base: float, 
                                   raio_km: float = 5.0) -> Tuple[float, float]:
        """Gera coordenadas com jitter aleatório ao redor de um ponto base."""
        delta_max = raio_km / 111.0
        delta_lat = random.uniform(-delta_max, delta_max)
        delta_lon = random.uniform(-delta_max, delta_max)
        return (lat_base + delta_lat, lon_base + delta_lon)
    
    def calcular_distancia_haversine(self, lat1: float, lon1: float, 
                                   lat2: float, lon2: float) -> float:
        """Calcula a distância entre dois pontos usando a fórmula de Haversine."""
        R = 6371  # Raio da Terra em km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def gerar_eventos_cronologicos(self) -> List[EventoALPR]:
        """
        Gera todos os eventos ALPR em ordem cronológica, lendo o número de infrações do DataFrame de veículos.
        Returns:
            List[EventoALPR]: Lista de eventos ordenados por timestamp
        """
        print(f"🎬 Gerando eventos cronológicos para {len(self.veiculos):,} veículos...")

        eventos = []
        timestamp_inicio = int(datetime.fromisoformat(
            self.config['timestamp_inicio']).timestamp() * 1000)
        intervalo_total_ms = self.config['intervalo_tempo_simulacao_horas'] * 3600 * 1000

        for _, veiculo in self.veiculos.iterrows():
            is_clonado = veiculo['clonado'] == 1
            num_infracoes = veiculo['num_infracoes'] if 'num_infracoes' in veiculo else 0

            # Escolher rota e timestamps
            rota = self.escolher_rota_realista(veiculo['cidade_emplacamento'], is_clonado)
            timestamps = self.gerar_timestamps_rota(rota, is_clonado, timestamp_inicio, intervalo_total_ms)

            # Criar eventos
            percentual_clones_identicos = self.config.get('percentual_clones_identicos', 0.3)
            for idx, (sensor, timestamp) in enumerate(zip(rota, timestamps)):
                semelhanca = self.calcular_semelhanca_visual(is_clonado, idx, len(rota), percentual_clones_identicos)
                evento = EventoALPR(
                    placa=veiculo['placa'],
                    timestamp=timestamp,
                    cam=sensor['cam'],
                    faixa=random.randint(1, sensor['faixas']),
                    lat=sensor['lat'],
                    lon=sensor['lon'],
                    is_clonado=is_clonado,
                    num_infracoes=num_infracoes,
                    semelhanca=semelhanca,
                    marca=veiculo.get('marca', ''),
                    modelo=veiculo.get('modelo', ''),
                    tipo=veiculo.get('tipo', ''),
                    cor=veiculo.get('cor', '')
                )
                eventos.append(evento)

        # Ordenar eventos por timestamp (CRUCIAL para streaming)
        eventos.sort(key=lambda x: x.timestamp)

        print(f"✅ {len(eventos):,} eventos gerados e ordenados cronologicamente")

        # Estatísticas temporais
        if eventos:
            inicio = pd.to_datetime(eventos[0].timestamp, unit='ms')
            fim = pd.to_datetime(eventos[-1].timestamp, unit='ms')
            duracao = fim - inicio

            print(f"   📅 Período: {inicio.strftime('%Y-%m-%d %H:%M')} até {fim.strftime('%Y-%m-%d %H:%M')}")
            print(f"   ⏱️ Duração: {duracao.total_seconds()/3600:.1f} horas")
            print(f"   📊 Taxa média: {len(eventos)/(duracao.total_seconds()/3600):.1f} eventos/hora")

        self.eventos_gerados = eventos
        return eventos
    
    def escolher_rota_realista(self, veiculo_cidade: str, is_clonado: bool = False) -> List[Dict]:
        """Escolhe uma rota realista de sensores para o veículo."""
        if is_clonado:
            return self._rota_clonada()
        else:
            return self._rota_normal(veiculo_cidade)
    
    def _rota_normal(self, cidade_origem: str) -> List[Dict]:
        """Gera rota normal para veículo legítimo."""
        sensores_cidade = [s for s in self.sensores if s['cidade'] == cidade_origem]
        
        if not sensores_cidade:
            sensores_disponiveis = self.sensores
        else:
            if random.random() < self.config['chance_de_rotas_urbanas']:
                sensores_disponiveis = sensores_cidade
            else:
                cidades_proximas = self._obter_cidades_proximas(cidade_origem)
                sensores_disponiveis = [s for s in self.sensores 
                                      if s['cidade'] in cidades_proximas]
        
        num_passagens = random.randint(
            self.config['n_passagens_min'],
            self.config['n_passagens_max']
        )
        
        if len(sensores_disponiveis) < num_passagens:
            return random.choices(sensores_disponiveis, k=num_passagens)
        else:
            return random.sample(sensores_disponiveis, num_passagens)
    
    def _rota_clonada(self) -> List[Dict]:
        """Gera rota inconsistente para veículo clonado."""
        num_passagens = random.randint(
            self.config['n_passagens_min'],
            min(self.config['n_passagens_max'], 8)
        )
        
        # Força passagens em locais geograficamente distantes
        cidades_distantes = ['Florianópolis', 'Chapecó', 'Joinville', 'Criciúma']
        sensores_distantes = []
        
        for cidade in cidades_distantes:
            sensores_cidade = [s for s in self.sensores if s['cidade'] == cidade]
            if sensores_cidade:
                sensores_distantes.extend(sensores_cidade[:2])
        
        if len(sensores_distantes) < num_passagens:
            sensores_distantes.extend(random.sample(self.sensores, 
                                                   num_passagens - len(sensores_distantes)))
        
        return random.sample(sensores_distantes, min(num_passagens, len(sensores_distantes)))
    
    def _obter_cidades_proximas(self, cidade: str, raio_km: float = 100) -> List[str]:
        """Retorna lista de cidades próximas."""
        if cidade not in self.config['lat_lon_por_cidade']:
            return [cidade]
        
        lat_origem, lon_origem = self.config['lat_lon_por_cidade'][cidade]
        cidades_proximas = [cidade]
        
        for outra_cidade, (lat, lon) in self.config['lat_lon_por_cidade'].items():
            if outra_cidade != cidade:
                distancia = self.calcular_distancia_haversine(lat_origem, lon_origem, lat, lon)
                if distancia <= raio_km:
                    cidades_proximas.append(outra_cidade)
        
        return cidades_proximas
    
    def gerar_timestamps_rota(self, rota: List[Dict], is_clonado: bool, 
                             timestamp_inicio: int, intervalo_total_ms: int) -> List[int]:
        """Gera timestamps realistas para uma rota."""
        inicio_simulacao = random.randint(
            timestamp_inicio,
            timestamp_inicio + intervalo_total_ms - 3600000
        )
        
        timestamps = [inicio_simulacao]
        timestamp_atual = inicio_simulacao
        
        for i in range(1, len(rota)):
            sensor_anterior = rota[i-1]
            sensor_atual = rota[i]
            
            distancia_km = self.calcular_distancia_haversine(
                sensor_anterior['lat'], sensor_anterior['lon'],
                sensor_atual['lat'], sensor_atual['lon']
            )
            
            if is_clonado:
                if distancia_km > 50:
                    intervalo_seg = random.randint(60, 300)  # Impossível
                else:
                    intervalo_seg = random.randint(300, 1800)
            else:
                if distancia_km <= 5:
                    intervalo_seg = random.randint(300, 1800)
                elif distancia_km <= 50:
                    intervalo_seg = random.randint(1800, 3600)
                else:
                    intervalo_seg = random.randint(3600, 7200)
            
            timestamp_futuro = timestamp_atual + (intervalo_seg * 1000)
            timestamp_limite = timestamp_inicio + intervalo_total_ms
            
            if timestamp_futuro > timestamp_limite:
                intervalo_seg = max(60, (timestamp_limite - timestamp_atual) // 1000)
            
            timestamp_atual += intervalo_seg * 1000
            timestamps.append(timestamp_atual)
        
        return timestamps
    
    def streaming_batch_completo(self) -> Generator[EventoALPR, None, None]:
        """
        Modo 1: Retorna todos os eventos de uma vez (para Random Forest tradicional).
        """
        print("📦 Iniciando modo: BATCH COMPLETO")
        
        if not self.eventos_gerados:
            self.gerar_eventos_cronologicos()
        
        for evento in self.eventos_gerados:
            yield evento
    
    def streaming_tempo_real(self, aceleracao: float = 1.0) -> Generator[EventoALPR, None, None]:
        """
        Modo 2: Streaming que respeita os intervalos temporais reais.
        
        Args:
            aceleracao: Fator de aceleração (1.0 = tempo real, 10.0 = 10x mais rápido)
        """
        print(f"⏰ Iniciando modo: STREAMING TEMPO REAL (aceleração: {aceleracao}x)")
        
        if not self.eventos_gerados:
            self.gerar_eventos_cronologicos()
        
        self.streaming_ativo = True
        timestamp_anterior = None
        
        for i, evento in enumerate(self.eventos_gerados):
            if not self.streaming_ativo:
                break
                
            if self.pausa_streaming:
                while self.pausa_streaming and self.streaming_ativo:
                    time.sleep(0.1)
            
            # Calcular delay baseado na diferença temporal real
            if timestamp_anterior is not None:
                delay_real = (evento.timestamp - timestamp_anterior) / 1000.0  # segundos
                delay_simulado = delay_real / aceleracao
                
                if delay_simulado > 0:
                    time.sleep(min(delay_simulado, 5.0))  # Máximo 5 segundos de espera
            
            timestamp_anterior = evento.timestamp
            
            # CORREÇÃO: timestamp_legivel em vez de timestamp_legible
            timestamp_legivel = pd.to_datetime(evento.timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
            print(f"📡 [{i+1:,}/{len(self.eventos_gerados):,}] "
                  f"{timestamp_legivel} - {evento.placa} - {evento.cam}")
            
            yield evento
    
    def streaming_janelas_temporais(self, tamanho_janela_horas: float = 1.0) -> Generator[List[EventoALPR], None, None]:
        """
        Modo 3: Streaming por janelas temporais (para algoritmos adaptativos).
        
        Args:
            tamanho_janela_horas: Tamanho da janela temporal em horas
        """
        print(f"🪟 Iniciando modo: JANELAS TEMPORAIS ({tamanho_janela_horas}h por janela)")
        
        if not self.eventos_gerados:
            self.gerar_eventos_cronologicos()
        
        janela_ms = int(tamanho_janela_horas * 3600 * 1000)
        timestamp_inicial = self.eventos_gerados[0].timestamp
        
        janela_atual = []
        timestamp_limite = timestamp_inicial + janela_ms
        janela_numero = 1
        
        for evento in self.eventos_gerados:
            if evento.timestamp <= timestamp_limite:
                janela_atual.append(evento)
            else:
                # Emitir janela atual
                if janela_atual:
                    inicio = pd.to_datetime(janela_atual[0].timestamp, unit='ms').strftime('%H:%M:%S')
                    fim = pd.to_datetime(janela_atual[-1].timestamp, unit='ms').strftime('%H:%M:%S')
                    print(f"📊 Janela {janela_numero}: {len(janela_atual):,} eventos ({inicio} - {fim})")
                    
                    yield janela_atual
                    janela_numero += 1
                
                # Iniciar nova janela
                janela_atual = [evento]
                timestamp_limite = evento.timestamp + janela_ms
        
        # Emitir última janela se houver eventos
        if janela_atual:
            inicio = pd.to_datetime(janela_atual[0].timestamp, unit='ms').strftime('%H:%M:%S')
            fim = pd.to_datetime(janela_atual[-1].timestamp, unit='ms').strftime('%H:%M:%S')
            print(f"📊 Janela {janela_numero}: {len(janela_atual):,} eventos ({inicio} - {fim})")
            yield janela_atual
    
    def streaming_acelerado_fixo(self, eventos_por_segundo: int = 10) -> Generator[EventoALPR, None, None]:
        """
        Modo 4: Streaming com taxa fixa de eventos por segundo.
        
        Args:
            eventos_por_segundo: Número de eventos a emitir por segundo
        """
        print(f"🚀 Iniciando modo: STREAMING ACELERADO ({eventos_por_segundo} eventos/seg)")
        
        if not self.eventos_gerados:
            self.gerar_eventos_cronologicos()
        
        self.streaming_ativo = True
        delay = 1.0 / eventos_por_segundo
        
        for i, evento in enumerate(self.eventos_gerados):
            if not self.streaming_ativo:
                break
            
            if self.pausa_streaming:
                while self.pausa_streaming and self.streaming_ativo:
                    time.sleep(0.1)
            
            time.sleep(delay)
            
            if i % 100 == 0:  # Log a cada 100 eventos
                # CORREÇÃO: timestamp_legivel em vez de timestamp_legible
                timestamp_legivel = pd.to_datetime(evento.timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
                print(f"📡 [{i+1:,}/{len(self.eventos_gerados):,}] "
                      f"{timestamp_legivel} - {evento.placa} - {evento.cam}")
            
            yield evento
    
    def parar_streaming(self):
        """Para o streaming atual."""
        self.streaming_ativo = False
        print("⏹️ Streaming interrompido")
    
    def pausar_streaming(self):
        """Pausa o streaming atual."""
        self.pausa_streaming = True
        print("⏸️ Streaming pausado")
    
    def retomar_streaming(self):
        """Retoma o streaming pausado."""
        self.pausa_streaming = False
        print("▶️ Streaming retomado")
    
    def salvar_eventos_csv(self, arquivo_saida: str = "passagens_streaming.csv") -> None:
        """Salva os eventos gerados em arquivo CSV."""
        if not self.eventos_gerados:
            print("❌ Nenhum evento gerado para salvar")
            return
        
        eventos_dict = [evento.to_dict() for evento in self.eventos_gerados]
        df_eventos = pd.DataFrame(eventos_dict)
        # Garante que a coluna 'semelhanca' está presente e exportada
        if 'semelhanca' not in df_eventos.columns:
            df_eventos['semelhanca'] = 1.0
        df_eventos.to_csv(arquivo_saida, index=False, encoding='utf-8')
        print(f"📁 Arquivo salvo: {arquivo_saida}")
        print(f"📊 Estatísticas dos eventos:")
        print(f"   🚗 Total de eventos: {len(df_eventos):,}")
        print(f"   🏷️ Placas distintas: {df_eventos['placa'].nunique():,}")
        print(f"   📡 Câmeras utilizadas: {df_eventos['cam'].nunique()}")
        print(f"   ⚠️ Eventos de veículos clonados: {df_eventos['is_clonado'].sum():,}")
        print(f"   🧬 Média de semelhança: {df_eventos['semelhanca'].mean():.3f}")
    
    def executar_simulacao_completa(self):
        """Executa a simulação completa e gera os eventos."""
        print(f"🎬 Iniciando simulação streaming ALPR completa")
        print(f"=" * 60)
        
        # Passo 1: Carregar veículos
        self.carregar_veiculos()
        
        # Passo 2: Distribuir sensores
        self.distribuir_sensores()
        
        # Passo 3: Gerar eventos cronológicos
        self.gerar_eventos_cronologicos()
        
        # Passo 4: Salvar eventos
        self.salvar_eventos_csv()
        
        print(f"=" * 60)
        print(f"🎉 Simulação concluída! Eventos prontos para streaming.")
        return self.eventos_gerados


def main():
    """Função principal - demonstração dos modos de streaming."""
    try:
        # Inicializar simulador
        simulador = SimuladorStreamingALPR("config.json")
        
        # Executar simulação completa
        eventos = simulador.executar_simulacao_completa()
        
        print(f"\n🎬 DEMONSTRAÇÃO DOS MODOS DE STREAMING:")
        print(f"=" * 60)
        
        # Demonstração 1: Batch completo (primeiros 10 eventos)
        print(f"\n1️⃣ MODO BATCH COMPLETO (primeiros 10 eventos):")
        batch_stream = simulador.streaming_batch_completo()
        for i, evento in enumerate(batch_stream):
            if i >= 10:
                break
            # CORREÇÃO: Usar o método to_dict() ou gerar timestamp_legivel
            timestamp_legivel = pd.to_datetime(evento.timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
            print(f"   📡 {timestamp_legivel} - {evento.placa} - {evento.cam}")
        
        # Demonstração 2: Janelas temporais (primeira janela)
        print(f"\n2️⃣ MODO JANELAS TEMPORAIS (primeira janela):")
        janelas_stream = simulador.streaming_janelas_temporais(tamanho_janela_horas=0.5)
        primeira_janela = next(janelas_stream)
        print(f"   📊 Primeira janela: {len(primeira_janela)} eventos")
        for evento in primeira_janela[:5]:
            # CORREÇÃO: Usar o método to_dict() ou gerar timestamp_legivel
            timestamp_legivel = pd.to_datetime(evento.timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
            print(f"      📡 {timestamp_legivel} - {evento.placa} - {evento.cam}")
        
        print(f"\n✅ Demonstração concluída!")
        print(f"💡 Para usar em produção:")
        print(f"   - streaming_batch_completo(): Random Forest tradicional")
        print(f"   - streaming_tempo_real(): Teste em tempo real")
        print(f"   - streaming_janelas_temporais(): Random Forest adaptativo")
        print(f"   - streaming_acelerado_fixo(): Testes de performance")
        
    except Exception as e:
        print(f"❌ Erro durante a simulação: {e}")
        raise


if __name__ == "__main__":
    main()