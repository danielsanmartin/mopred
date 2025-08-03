"""
Gerador de Veículos Simulados
=============================

Script para gerar um conjunto simulado de veículos com base em um arquivo JSON
de especificação de características (caracteristicas_veiculos.json).

Gera arquivo veiculos_gerados.csv com veículos realistas e consistentes.

Autor: Sistema ALPR
Data: 2025
"""

import pandas as pd
import json
import random
import string
import os
from typing import Dict, List, Set, Tuple

class GeradorVeiculos:
    def __init__(self, arquivo_caracteristicas: str = "caracteristicas_veiculos.json"):
        """
        Inicializa o gerador de veículos.
        
        Args:
            arquivo_caracteristicas (str): Caminho para o arquivo JSON com especificações
        """
        self.caracteristicas = self.carregar_caracteristicas(arquivo_caracteristicas)
        self.placas_geradas: Set[str] = set()
        
        # Configurações padrão
        self.total_veiculos = 10000
        self.percentual_clonados = 0.002  # 0.2%
        
        print(f"✅ Gerador inicializado com {len(self.caracteristicas['marca_modelo_tipo']['valores_possiveis'])} marcas")
    
    def carregar_caracteristicas(self, arquivo: str) -> Dict:
        """
        Carrega o arquivo JSON com as características dos veículos.
        
        Args:
            arquivo (str): Caminho para o arquivo JSON
            
        Returns:
            Dict: Dicionário com as características carregadas
        """
        if not os.path.exists(arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            caracteristicas = json.load(f)
        
        print(f"✅ Características carregadas de {arquivo}")
        return caracteristicas
    
    def gerar_placa_mercosul(self) -> str:
        """
        Gera uma placa no padrão Mercosul brasileiro (ABC1D23).
        
        Returns:
            str: Placa no formato Mercosul
        """
        while True:
            # Formato Mercosul: 3 letras + 1 número + 1 letra + 2 números
            letras1 = ''.join(random.choices(string.ascii_uppercase, k=3))
            numero1 = random.choice(string.digits)
            letra2 = random.choice(string.ascii_uppercase)
            numeros2 = ''.join(random.choices(string.digits, k=2))
            
            placa = f"{letras1}{numero1}{letra2}{numeros2}"
            
            # Verifica se a placa é única
            if placa not in self.placas_geradas:
                self.placas_geradas.add(placa)
                return placa
    
    def sortear_marca_modelo_tipo(self) -> Tuple[str, str, str]:
        """
        Sorteia uma combinação válida de marca, modelo e tipo.
        
        Returns:
            Tuple[str, str, str]: Tupla com (marca, modelo, tipo)
        """
        marcas_disponeis = list(self.caracteristicas['marca_modelo_tipo']['valores_possiveis'].keys())
        marca = random.choice(marcas_disponeis)
        
        modelos_marca = self.caracteristicas['marca_modelo_tipo']['valores_possiveis'][marca]
        modelo = random.choice(list(modelos_marca.keys()))
        
        tipo = modelos_marca[modelo]
        
        return marca, modelo, tipo
    
    def sortear_ano(self) -> int:
        """
        Sorteia um ano de fabricação realista.
        
        Returns:
            int: Ano de fabricação entre 2005 e 2025
        """
        # Distribuição mais realista: mais veículos recentes
        anos_recentes = list(range(2018, 2026))  # 2018-2025
        anos_antigos = list(range(2005, 2018))   # 2005-2017
        
        # 70% de chance de ser um carro mais recente
        if random.random() < 0.7:
            return random.choice(anos_recentes)
        else:
            return random.choice(anos_antigos)
    
    def sortear_cor(self) -> str:
        """
        Sorteia uma cor do veículo com distribuição realista.
        
        Returns:
            str: Cor do veículo
        """
        cores = self.caracteristicas['cor']['valores_possiveis']
        
        # Distribuição mais realista das cores (baseada no mercado brasileiro)
        cores_comuns = ['branco', 'prata', 'preto', 'cinza']
        cores_menos_comuns = ['vermelho', 'azul', 'verde', 'amarelo', 'marrom', 'laranja']
        
        # 80% de chance de ser uma cor comum
        if random.random() < 0.8:
            return random.choice(cores_comuns)
        else:
            return random.choice(cores_menos_comuns)
    
    def sortear_categoria(self) -> str:
        """
        Sorteia uma categoria com distribuição realista.
        
        Returns:
            str: Categoria do veículo
        """
        categorias = self.caracteristicas['categoria']['valores_possiveis']
        
        # Distribuição realista: maioria particular
        if random.random() < 0.85:
            return 'particular'
        elif random.random() < 0.95:
            return 'aluguel'
        elif random.random() < 0.98:
            return 'oficial'
        else:
            return 'colecionador'
    
    def sortear_combustivel(self, tipo: str) -> str:
        """
        Sorteia o tipo de combustível baseado no tipo do veículo.
        
        Args:
            tipo (str): Tipo do veículo
            
        Returns:
            str: Tipo de combustível
        """
        combustiveis = self.caracteristicas['combustivel']['valores_possiveis']
        
        if tipo == 'moto':
            # Motos usam principalmente gasolina ou flex
            return random.choice(['gasolina', 'flex'])
        elif tipo == 'caminhão':
            # Caminhões usam principalmente diesel
            return random.choice(['diesel', 'diesel']) if random.random() < 0.9 else 'flex'
        else:
            # Carros de passeio, SUVs, utilitários
            # Distribuição realista: muito flex, pouco gasolina pura, alguns diesel
            rand = random.random()
            if rand < 0.7:
                return 'flex'
            elif rand < 0.85:
                return 'gasolina'
            elif rand < 0.95:
                return 'diesel'
            elif rand < 0.98:
                return 'álcool'
            else:
                return 'elétrico'
    
    def sortear_cidade_emplacamento(self) -> str:
        """
        Sorteia uma cidade de emplacamento com distribuição realista.
        
        Returns:
            str: Cidade de emplacamento
        """
        cidades = self.caracteristicas['cidade_emplacamento']['valores_possiveis']
        
        # Distribuição baseada no tamanho das cidades (mais veículos em cidades maiores)
        cidades_grandes = ['Florianópolis', 'Joinville', 'Blumenau', 'Chapecó', 'Itajaí']
        cidades_medias = ['São José', 'Criciúma', 'Lages', 'Palhoça', 'Balneário Camboriú']
        cidades_pequenas = ['Jaraguá do Sul', 'Brusque', 'Tubarão', 'Caçador', 'Concórdia',
                           'Xanxerê', 'Araranguá', 'Rio do Sul', 'Laguna', 'Canoinhas']
        
        rand = random.random()
        if rand < 0.5:  # 50% nas cidades grandes
            return random.choice(cidades_grandes)
        elif rand < 0.8:  # 30% nas cidades médias
            return random.choice(cidades_medias)
        else:  # 20% nas cidades pequenas
            return random.choice(cidades_pequenas)
    
    def determinar_clonado(self, indice: int) -> int:
        """
        Determina se o veículo será marcado como clonado.
        
        Args:
            indice (int): Índice do veículo na sequência de geração
            
        Returns:
            int: 1 se clonado, 0 se normal
        """
        num_clonados = int(self.total_veiculos * self.percentual_clonados)
        return 1 if indice < num_clonados else 0
    
    def gerar_veiculo(self, indice: int,
                      intervalo_infracoes_clonado: tuple = None,
                      intervalo_infracoes_normal: tuple = None) -> Dict:
        """
        Gera um veículo completo com todas as características, incluindo número de infrações.
        Permite configurar os intervalos de infrações para clonados e não clonados.
        Args:
            indice (int): Índice do veículo na sequência
            intervalo_infracoes_clonado: (min, max) para veículos clonados
            intervalo_infracoes_normal: (min, max) para veículos normais
        Returns:
            Dict: Dicionário com todas as características do veículo
        """
        # Permitir configuração via config.json
        if intervalo_infracoes_clonado is None:
            intervalo_infracoes_clonado = tuple(self.caracteristicas.get('intervalo_infracoes_clonado', (5, 20)))
        if intervalo_infracoes_normal is None:
            intervalo_infracoes_normal = tuple(self.caracteristicas.get('intervalo_infracoes_normal', (0, 3)))

        # Gera placa única
        placa = self.gerar_placa_mercosul()

        # Sorteia marca, modelo e tipo (consistentes entre si)
        marca, modelo, tipo = self.sortear_marca_modelo_tipo()

        # Sorteia outras características
        ano = self.sortear_ano()
        cor = self.sortear_cor()
        categoria = self.sortear_categoria()
        combustivel = self.sortear_combustivel(tipo)
        cidade_emplacamento = self.sortear_cidade_emplacamento()
        clonado = self.determinar_clonado(indice)

        # Define número de infrações conforme tipo
        if clonado:
            num_infracoes = random.randint(*intervalo_infracoes_clonado)
        else:
            num_infracoes = random.randint(*intervalo_infracoes_normal)

        return {
            'placa': placa,
            'marca': marca,
            'modelo': modelo,
            'tipo': tipo,
            'ano': ano,
            'cor': cor,
            'categoria': categoria,
            'combustivel': combustivel,
            'cidade_emplacamento': cidade_emplacamento,
            'clonado': clonado,
            'num_infracoes': num_infracoes
        }
    
    def gerar_conjunto_veiculos(self, total: int = None, percentual_clonados: float = None,
                                intervalo_infracoes_clonado: tuple = None,
                                intervalo_infracoes_normal: tuple = None) -> pd.DataFrame:
        """
        Gera um conjunto completo de veículos simulados.
        
        Args:
            total (int, optional): Número total de veículos. Usa self.total_veiculos se None.
            percentual_clonados (float, optional): Percentual de clonados. Usa self.percentual_clonados se None.
            
        Returns:
            pd.DataFrame: DataFrame com todos os veículos gerados
        """
        if total is not None:
            self.total_veiculos = total
        if percentual_clonados is not None:
            self.percentual_clonados = percentual_clonados
        
        print(f"🚀 Gerando {self.total_veiculos:,} veículos...")
        print(f"   ⚠️ Percentual de clonados: {self.percentual_clonados:.1%}")
        
        veiculos = []
        
        # Gera veículos clonados primeiro para garantir o percentual exato
        num_clonados = int(self.total_veiculos * self.percentual_clonados)
        print(f"   📊 Veículos clonados: {num_clonados}")
        
        for i in range(self.total_veiculos):
            veiculo = self.gerar_veiculo(i,
                                        intervalo_infracoes_clonado=intervalo_infracoes_clonado,
                                        intervalo_infracoes_normal=intervalo_infracoes_normal)
            veiculos.append(veiculo)
            # Progress feedback
            if (i + 1) % 1000 == 0:
                print(f"   📈 Progresso: {i+1:,}/{self.total_veiculos:,} ({(i+1)/self.total_veiculos*100:.1f}%)")
        
        # Embaralha a lista para misturar clonados e normais
        random.shuffle(veiculos)
        
        df = pd.DataFrame(veiculos)
        
        print(f"✅ Geração concluída!")
        return df
    
    def salvar_csv(self, df: pd.DataFrame, arquivo_saida: str = "veiculos_gerados.csv") -> None:
        """
        Salva o DataFrame de veículos em um arquivo CSV.
        
        Args:
            df (pd.DataFrame): DataFrame com os veículos
            arquivo_saida (str): Nome do arquivo de saída
        """
        df.to_csv(arquivo_saida, index=False, encoding='utf-8')
        
        print(f"📁 Arquivo salvo: {arquivo_saida}")
        print(f"📊 Estatísticas finais:")
        print(f"   🚗 Total de veículos: {len(df):,}")
        print(f"   🏷️  Placas únicas: {df['placa'].nunique():,}")
        print(f"   ⚠️  Veículos clonados: {df['clonado'].sum():,} ({df['clonado'].mean():.1%})")
        print(f"   🏭 Marcas distintas: {df['marca'].nunique()}")
        print(f"   🚙 Modelos distintos: {df['modelo'].nunique()}")
        print(f"   🏙️  Cidades distintas: {df['cidade_emplacamento'].nunique()}")
        
        # Estatísticas por categoria
        print(f"\n📈 Distribuição por tipo:")
        tipo_stats = df['tipo'].value_counts()
        for tipo, count in tipo_stats.items():
            print(f"   {tipo}: {count:,} ({count/len(df)*100:.1f}%)")
        
        print(f"\n🎨 Distribuição por cor:")
        cor_stats = df['cor'].value_counts()
        for cor, count in cor_stats.head(5).items():
            print(f"   {cor}: {count:,} ({count/len(df)*100:.1f}%)")
    
    def validar_dados(self, df: pd.DataFrame) -> bool:
        """
        Valida a consistência dos dados gerados.
        
        Args:
            df (pd.DataFrame): DataFrame para validar
            
        Returns:
            bool: True se todos os dados estão válidos
        """
        print(f"🔍 Validando dados gerados...")
        
        erros = []
        
        # Verifica placas únicas
        if df['placa'].nunique() != len(df):
            erros.append("Placas duplicadas encontradas")
        
        # Verifica formato das placas (Mercosul)
        placas_invalidas = df[~df['placa'].str.match(r'^[A-Z]{3}\d[A-Z]\d{2}$')]
        if len(placas_invalidas) > 0:
            erros.append(f"{len(placas_invalidas)} placas com formato inválido")
        
        # Verifica consistência marca-modelo-tipo
        marca_modelo_tipo = self.caracteristicas['marca_modelo_tipo']['valores_possiveis']
        for _, veiculo in df.iterrows():
            marca = veiculo['marca']
            modelo = veiculo['modelo']
            tipo = veiculo['tipo']
            
            if marca not in marca_modelo_tipo:
                erros.append(f"Marca inválida: {marca}")
                break
            elif modelo not in marca_modelo_tipo[marca]:
                erros.append(f"Modelo {modelo} inválido para marca {marca}")
                break
            elif marca_modelo_tipo[marca][modelo] != tipo:
                erros.append(f"Tipo {tipo} inconsistente para {marca} {modelo}")
                break
        
        # Verifica anos válidos
        anos_invalidos = df[(df['ano'] < 2005) | (df['ano'] > 2025)]
        if len(anos_invalidos) > 0:
            erros.append(f"{len(anos_invalidos)} veículos com ano inválido")
        
        # Verifica valores válidos para campos categóricos
        campos_categoricos = ['cor', 'categoria', 'combustivel', 'cidade_emplacamento']
        for campo in campos_categoricos:
            valores_validos = self.caracteristicas[campo]['valores_possiveis']
            valores_invalidos = df[~df[campo].isin(valores_validos)]
            if len(valores_invalidos) > 0:
                erros.append(f"{len(valores_invalidos)} valores inválidos em {campo}")
        
        if erros:
            print(f"❌ Erros encontrados:")
            for erro in erros:
                print(f"   - {erro}")
            return False
        else:
            print(f"✅ Todos os dados estão válidos!")
            return True


def main():
    """Função principal para execução do gerador."""
    try:
        # Configurações
        TOTAL_VEICULOS = 10000
        PERCENTUAL_CLONADOS = 0.003
        ARQUIVO_SAIDA = "veiculos_gerados.csv"
        
        print(f"🏭 Iniciando geração de veículos simulados")
        print(f"📋 Configurações:")
        print(f"   Total de veículos: {TOTAL_VEICULOS:,}")
        print(f"   Percentual clonados: {PERCENTUAL_CLONADOS:.1%}")
        print(f"   Arquivo de saída: {ARQUIVO_SAIDA}")
        print()
        
        # Inicializa gerador
        gerador = GeradorVeiculos("caracteristicas_veiculos.json")
        
        # Gera conjunto de veículos
        df_veiculos = gerador.gerar_conjunto_veiculos(
            total=TOTAL_VEICULOS,
            percentual_clonados=PERCENTUAL_CLONADOS
        )
        
        # Valida os dados
        dados_validos = gerador.validar_dados(df_veiculos)
        
        if dados_validos:
            # Salva arquivo CSV
            gerador.salvar_csv(df_veiculos, ARQUIVO_SAIDA)
            print(f"\n🎉 Processo concluído com sucesso!")
        else:
            print(f"\n❌ Processo interrompido devido a erros de validação.")
            
    except Exception as e:
        print(f"❌ Erro durante a geração: {e}")
        raise


if __name__ == "__main__":
    main()
