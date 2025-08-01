"""
Simulador de Passagens ALPR
===========================

Script para simular passagens de veículos por sensores ALPR com base em:
- config.json: parâmetros da simulação
- veiculos_gerados.csv: lista de veículos (incluindo clonados)

Gera arquivo passagens.csv com registros de capturas por câmeras.

Autor: Sistema ALPR
Data: 2025
"""

import pandas as pd
import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import os

class SimuladorALPR:
    def __init__(self, config_path: str = "config.json"):
        """
        Inicializa o simulador ALPR.
        
        Args:
            config_path (str): Caminho para o arquivo de configuração
        """
        self.config = self.carregar_config(config_path)
        self.sensores = []
        self.veiculos = pd.DataFrame()
        self.passagens = []
        
        print(f"✅ Simulador ALPR inicializado")
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
    
    def gerar_coordenada_com_jitter(self, lat_base: float, lon_base: float, 
                                   raio_km: float = 5.0) -> Tuple[float, float]:
        """
        Gera coordenadas com jitter aleatório ao redor de um ponto base.
        
        Args:
            lat_base (float): Latitude base
            lon_base (float): Longitude base
            raio_km (float): Raio máximo do jitter em km
            
        Returns:
            Tuple[float, float]: Nova coordenada (lat, lon)
        """
        # Conversão aproximada: 1 grau ≈ 111 km
        delta_max = raio_km / 111.0
        
        delta_lat = random.uniform(-delta_max, delta_max)
        delta_lon = random.uniform(-delta_max, delta_max)
        
        return (lat_base + delta_lat, lon_base + delta_lon)
    
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
                    'faixas': random.randint(1, 4)  # 1 a 4 faixas por sensor
                }
                
                self.sensores.append(sensor)
                sensor_id += 1
        
        print(f"✅ {len(self.sensores)} sensores distribuídos")
        print(f"   📊 Por cidade:")
        for cidade, quantidade in self.config['sensores_por_cidade'].items():
            print(f"      {cidade}: {quantidade} sensores")
    
    def calcular_distancia_haversine(self, lat1: float, lon1: float, 
                                   lat2: float, lon2: float) -> float:
        """
        Calcula a distância entre dois pontos usando a fórmula de Haversine.
        
        Returns:
            float: Distância em quilômetros
        """
        R = 6371  # Raio da Terra em km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distancia = R * c
        
        return distancia
    
    def escolher_rota_realista(self, veiculo_cidade: str, is_clonado: bool = False) -> List[Dict]:
        """
        Escolhe uma rota realista de sensores para o veículo.
        
        Args:
            veiculo_cidade (str): Cidade de emplacamento do veículo
            is_clonado (bool): Se é um veículo clonado
            
        Returns:
            List[Dict]: Lista de sensores na rota
        """
        if is_clonado:
            # Veículos clonados: rota inconsistente (locais distantes)
            return self._rota_clonada()
        else:
            # Veículos normais: rota coerente
            return self._rota_normal(veiculo_cidade)
    
    def _rota_normal(self, cidade_origem: str) -> List[Dict]:
        """Gera rota normal para veículo legítimo."""
        sensores_cidade = [s for s in self.sensores if s['cidade'] == cidade_origem]
        
        if not sensores_cidade:
            # Se não há sensores na cidade, pega qualquer um
            sensores_disponiveis = self.sensores
        else:
            # 80% chance de rota urbana, 20% intermunicipal
            if random.random() < self.config['chance_de_rotas_urbanas']:
                # Rota urbana: sensores da mesma cidade
                sensores_disponiveis = sensores_cidade
            else:
                # Rota intermunicipal: pode incluir outras cidades próximas
                cidades_proximas = self._obter_cidades_proximas(cidade_origem)
                sensores_disponiveis = [s for s in self.sensores 
                                      if s['cidade'] in cidades_proximas]
        
        # Escolhe quantos sensores para a rota
        num_passagens = random.randint(
            self.config['n_passagens_min'],
            self.config['n_passagens_max']
        )
        
        # Seleciona sensores aleatórios
        if len(sensores_disponiveis) < num_passagens:
            return random.choices(sensores_disponiveis, k=num_passagens)
        else:
            return random.sample(sensores_disponiveis, num_passagens)
    
    def _rota_clonada(self) -> List[Dict]:
        """Gera rota inconsistente para veículo clonado."""
        num_passagens = random.randint(
            self.config['n_passagens_min'],
            min(self.config['n_passagens_max'], 8)  # Limita para não ser muito óbvio
        )
        
        # Força passagens em locais geograficamente distantes
        sensores_distantes = []
        
        # Pega algumas cidades bem distantes
        cidades_distantes = ['Florianópolis', 'Chapecó', 'Joinville', 'Criciúma']
        
        for cidade in cidades_distantes:
            sensores_cidade = [s for s in self.sensores if s['cidade'] == cidade]
            if sensores_cidade:
                sensores_distantes.extend(sensores_cidade[:2])  # Máximo 2 por cidade
        
        if len(sensores_distantes) < num_passagens:
            # Completa com sensores aleatórios
            sensores_distantes.extend(random.sample(self.sensores, 
                                                   num_passagens - len(sensores_distantes)))
        
        return random.sample(sensores_distantes, min(num_passagens, len(sensores_distantes)))
    
    def _obter_cidades_proximas(self, cidade: str, raio_km: float = 100) -> List[str]:
        """Retorna lista de cidades próximas."""
        if cidade not in self.config['lat_lon_por_cidade']:
            return [cidade]
        
        lat_origem, lon_origem = self.config['lat_lon_por_cidade'][cidade]
        cidades_proximas = [cidade]  # Inclui a própria cidade
        
        for outra_cidade, (lat, lon) in self.config['lat_lon_por_cidade'].items():
            if outra_cidade != cidade:
                distancia = self.calcular_distancia_haversine(lat_origem, lon_origem, lat, lon)
                if distancia <= raio_km:
                    cidades_proximas.append(outra_cidade)
        
        return cidades_proximas
    
    def gerar_timestamps_rota(self, rota: List[Dict], is_clonado: bool = False) -> List[int]:
        """
        Gera timestamps realistas para uma rota.
        
        Args:
            rota (List[Dict]): Lista de sensores na rota
            is_clonado (bool): Se é veículo clonado
            
        Returns:
            List[int]: Lista de timestamps em milissegundos
        """
        timestamp_inicio = int(datetime.fromisoformat(
            self.config['timestamp_inicio']).timestamp() * 1000)
        intervalo_total_ms = self.config['intervalo_tempo_simulacao_horas'] * 3600 * 1000
        
        # Início aleatório dentro do período de simulação
        inicio_simulacao = random.randint(
            timestamp_inicio,
            timestamp_inicio + intervalo_total_ms - 3600000  # Deixa pelo menos 1h para a rota
        )
        
        timestamps = [inicio_simulacao]
        timestamp_atual = inicio_simulacao
        
        for i in range(1, len(rota)):
            sensor_anterior = rota[i-1]
            sensor_atual = rota[i]
            
            # Calcula distância entre sensores
            distancia_km = self.calcular_distancia_haversine(
                sensor_anterior['lat'], sensor_anterior['lon'],
                sensor_atual['lat'], sensor_atual['lon']
            )
            
            if is_clonado:
                # Veículo clonado: intervalos inconsistentes
                if distancia_km > 50:  # Distância grande
                    # Tempo muito curto para distância grande (impossível)
                    intervalo_seg = random.randint(60, 300)  # 1-5 minutos
                else:
                    # Tempo normal para distâncias pequenas
                    intervalo_seg = random.randint(300, 1800)  # 5-30 minutos
            else:
                # Veículo normal: tempo proporcional à distância
                if distancia_km <= 5:  # Distância urbana
                    intervalo_seg = random.randint(300, 1800)  # 5-30 minutos
                elif distancia_km <= 50:  # Distância intermunicipal curta
                    intervalo_seg = random.randint(1800, 3600)  # 30-60 minutos
                else:  # Distância intermunicipal longa
                    intervalo_seg = random.randint(3600, 7200)  # 1-2 horas
            
            # Verifica se o tempo calculado não excede o fim da simulação
            timestamp_futuro = timestamp_atual + (intervalo_seg * 1000)
            timestamp_limite = timestamp_inicio + intervalo_total_ms
            
            if timestamp_futuro > timestamp_limite:
                # Ajusta o intervalo para não exceder o limite
                intervalo_seg = max(60, (timestamp_limite - timestamp_atual) // 1000)
            
            timestamp_atual += intervalo_seg * 1000
            timestamps.append(timestamp_atual)
        
        return timestamps
    
    def simular_veiculo(self, veiculo: Dict) -> List[Dict]:
        """
        Simula as passagens de um veículo específico.
        
        Args:
            veiculo (Dict): Dados do veículo
            
        Returns:
            List[Dict]: Lista de passagens simuladas
        """
        try:
            is_clonado = veiculo['clonado'] == 1
            
            # Escolhe rota de sensores
            rota = self.escolher_rota_realista(veiculo['cidade_emplacamento'], is_clonado)
            
            if not rota:
                return []
            
            # Gera timestamps para a rota
            timestamps = self.gerar_timestamps_rota(rota, is_clonado)
            
            # Cria passagens
            passagens_veiculo = []
            for i, (sensor, timestamp) in enumerate(zip(rota, timestamps)):
                faixa = random.randint(1, sensor['faixas'])
                
                passagem = {
                    'placa': veiculo['placa'],
                    'timestamp': timestamp,
                    'cam': sensor['cam'],
                    'faixa': faixa,
                    'lat': sensor['lat'],
                    'lon': sensor['lon']
                }
                
                passagens_veiculo.append(passagem)
            
            return passagens_veiculo
            
        except Exception as e:
            print(f"⚠️  Erro ao simular veículo {veiculo['placa']}: {e}")
            return []
    
    def simular_passagens(self) -> None:
        """Simula passagens para todos os veículos."""
        print(f"🚗 Simulando passagens para {len(self.veiculos):,} veículos...")
        
        self.passagens = []
        veiculos_processados = 0
        
        for _, veiculo in self.veiculos.iterrows():
            passagens_veiculo = self.simular_veiculo(veiculo.to_dict())
            self.passagens.extend(passagens_veiculo)
            
            veiculos_processados += 1
            if veiculos_processados % 1000 == 0:
                print(f"   📈 Progresso: {veiculos_processados:,}/{len(self.veiculos):,} "
                      f"({veiculos_processados/len(self.veiculos)*100:.1f}%)")
        
        print(f"✅ Simulação concluída!")
        print(f"   📊 Total de passagens: {len(self.passagens):,}")
        print(f"   📡 Sensores utilizados: {len(set(p['cam'] for p in self.passagens))}")
    
    def salvar_passagens(self, arquivo_saida: str = "passagens.csv") -> None:
        """Salva as passagens em arquivo CSV."""
        if not self.passagens:
            print("❌ Nenhuma passagem para salvar")
            return
        
        df_passagens = pd.DataFrame(self.passagens)
        
        # Ordena por timestamp
        df_passagens = df_passagens.sort_values('timestamp').reset_index(drop=True)
        
        # Converte timestamp para formato legível
        df_passagens['timestamp_legivel'] = pd.to_datetime(
            df_passagens['timestamp'], unit='ms'
        ).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Salva arquivo
        df_passagens.to_csv(arquivo_saida, index=False, encoding='utf-8')
        
        print(f"📁 Arquivo salvo: {arquivo_saida}")
        print(f"📊 Estatísticas das passagens:")
        print(f"   🚗 Total de passagens: {len(df_passagens):,}")
        print(f"   🏷️  Placas distintas: {df_passagens['placa'].nunique():,}")
        print(f"   📡 Câmeras utilizadas: {df_passagens['cam'].nunique()}")
        print(f"   🏙️  Cidades cobertas: {len(set(s['cidade'] for s in self.sensores))}")
        
        # Estatísticas temporais
        inicio = df_passagens['timestamp'].min()
        fim = df_passagens['timestamp'].max()
        duracao_horas = (fim - inicio) / (1000 * 3600)
        print(f"   ⏱️  Período: {duracao_horas:.1f} horas")
        
        # Passagens por veículo clonado vs normal
        veiculos_clonados = set(self.veiculos[self.veiculos['clonado'] == 1]['placa'])
        passagens_clonados = len(df_passagens[df_passagens['placa'].isin(veiculos_clonados)])
        passagens_normais = len(df_passagens) - passagens_clonados
        
        print(f"   ✅ Passagens normais: {passagens_normais:,}")
        print(f"   ⚠️  Passagens clonados: {passagens_clonados:,}")
    
    def executar_simulacao(self) -> None:
        """Executa a simulação completa."""
        print(f"🎬 Iniciando simulação ALPR completa")
        print(f"=" * 50)
        
        # Passo 1: Carregar veículos
        self.carregar_veiculos()
        
        # Passo 2: Distribuir sensores
        self.distribuir_sensores()
        
        # Passo 3: Simular passagens
        self.simular_passagens()
        
        # Passo 4: Salvar resultados
        self.salvar_passagens()
        
        print(f"=" * 50)
        print(f"🎉 Simulação concluída com sucesso!")


def main():
    """Função principal."""
    try:
        # Inicializa simulador
        simulador = SimuladorALPR("config.json")
        
        # Executa simulação completa
        simulador.executar_simulacao()
        
    except Exception as e:
        print(f"❌ Erro durante a simulação: {e}")
        raise


if __name__ == "__main__":
    main()