"""
PocketOptionAPI - Interface Python não oficial para a plataforma PocketOption

Esta é a implementação principal da API da PocketOption, fornecendo métodos
para autenticação, trading e obtenção de dados do mercado.

Versão: 1.0.0
"""

import asyncio
import threading
import sys
from tzlocal import get_localzone
import json
from pocketoptionapi.api import PocketOptionAPI
import pocketoptionapi.constants as OP_code
import time
import logging
import operator
import pocketoptionapi.global_value as global_value
from collections import defaultdict
from collections import deque
import pandas as pd

# Obtém o fuso horário local do sistema como uma string no formato IANA
local_zone_name = get_localzone()

def nested_dict(n, type):
    """
    Cria um dicionário aninhado com profundidade n.
    
    Args:
        n (int): Número de níveis de aninhamento
        type: Tipo do valor final no dicionário
    
    Returns:
        defaultdict: Dicionário aninhado inicializado
    """
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))

def get_balance():
    """Retorna o saldo atual da conta."""
    return global_value.balance

class PocketOption:
    """
    Classe principal para interação com a PocketOption.
    
    Fornece métodos para:
    - Conexão e autenticação
    - Trading (compra/venda)
    - Obtenção de dados do mercado
    - Gerenciamento de conta
    
    Attributes:
        __version__ (str): Versão atual da API
        ssid (str): ID de sessão para autenticação
        demo (bool): Se True, usa conta demo. Se False, usa conta real
    """
    
    __version__ = "1.0.0"

    def __init__(self, ssid, demo):
        """
        Inicializa uma nova instância da API PocketOption.
        
        Args:
            ssid (str): ID de sessão para autenticação
            demo (bool): Se True, usa conta demo. Se False, usa conta real
        """
        # Timeframes disponíveis em segundos
        self.size = [1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800,
                     3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000]
        global_value.SSID = ssid
        global_value.DEMO = demo
        print(f"Modo Demo: {demo}")
        self.suspend = 0.5
        self.thread = None
        self.subscribe_candle = []
        self.subscribe_candle_all_size = []
        self.subscribe_mood = []
        # Dados para operações digitais
        self.get_digital_spot_profit_after_sale_data = nested_dict(2, int)
        self.get_realtime_strike_list_temp_data = {}
        self.get_realtime_strike_list_temp_expiration = 0
        self.SESSION_HEADER = {
            "User-Agent": r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          r"Chrome/66.0.3359.139 Safari/537.36"}
        self.SESSION_COOKIE = {}
        self.api = PocketOptionAPI()
        self.loop = asyncio.get_event_loop()

    def get_server_timestamp(self):
        """Retorna o timestamp atual do servidor em segundos."""
        return self.api.time_sync.server_timestamp
        
    def Stop(self):
        """Para a execução do programa."""
        sys.exit()

    def get_server_datetime(self):
        """Retorna o datetime atual do servidor."""
        return self.api.time_sync.server_datetime

    def set_session(self, header, cookie):
        """
        Define os headers e cookies da sessão.
        
        Args:
            header (dict): Headers HTTP para requisições
            cookie (dict): Cookies para autenticação
        """
        self.SESSION_HEADER = header
        self.SESSION_COOKIE = cookie

    def get_async_order(self, buy_order_id):
        """
        Obtém informações de uma ordem assíncrona.
        
        Args:
            buy_order_id (int): ID da ordem de compra
            
        Returns:
            dict: Informações da ordem ou None se não encontrada
        """
        if self.api.order_async["deals"][0]["id"] == buy_order_id:
            return self.api.order_async["deals"][0]
        else:
            return None

    def get_async_order_id(self, buy_order_id):
        return self.api.order_async["deals"][0][buy_order_id]

    def start_async(self):
        """Inicia a conexão assíncrona com o WebSocket."""
        asyncio.run(self.api.connect())
        
    def disconnect(self):
        """
        Fecha graciosamente a conexão WebSocket e limpa recursos.
        
        Este método:
        1. Fecha a conexão WebSocket
        2. Cancela todas as tasks pendentes
        3. Fecha o loop de eventos
        4. Encerra a thread do WebSocket
        """
        try:
            if global_value.websocket_is_connected:
                asyncio.run(self.api.close())
                print("Conexão WebSocket fechada com sucesso.")
            else:
                print("WebSocket não estava conectado.")

            if self.loop is not None:
                for task in asyncio.all_tasks(self.loop):
                    task.cancel()

                if not self.loop.is_closed():
                    self.loop.stop()
                    self.loop.close()
                    print("Loop de eventos parado e fechado com sucesso.")

            if self.api.websocket_thread is not None and self.api.websocket_thread.is_alive():
                self.api.websocket_thread.join()
                print("Thread WebSocket encerrada com sucesso.")

        except Exception as e:
            print(f"Erro durante a desconexão: {e}")

    def connect(self):
        """
        Estabelece conexão com a API da PocketOption.
        
        Este método inicia uma thread separada para manter a conexão WebSocket.
        
        Returns:
            bool: True se a conexão foi iniciada com sucesso, False caso contrário
        """
        try:
            websocket_thread = threading.Thread(target=self.api.connect, daemon=True)
            websocket_thread.start()

        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
        return True
    
    def GetPayout(self, pair):
        """
        Obtém o payout (retorno percentual) para um par de moedas.
        
        Args:
            pair (str): Par de moedas (ex: "EURUSD")
            
        Returns:
            float: Percentual de payout ou None se não disponível
        """
        try:
            data = self.api.GetPayoutData()
            data = json.loads(data)
            data2 = None
            for i in data:
                if i[1] == pair:
                    data2 = i
            return data2[5]
        except:
            return None

    @staticmethod
    def check_connect():
        """
        Verifica se a conexão WebSocket está ativa.
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        if global_value.websocket_is_connected == 0:
            return False
        elif global_value.websocket_is_connected is None:
            return False
        else:
            return True

    @staticmethod
    def get_balance():
        """
        Obtém o saldo atual da conta.
        
        Returns:
            float: Saldo atual ou None se não disponível
        """
        if global_value.balance_updated:
            return global_value.balance
        else:
            return None
            
    @staticmethod
    def check_open():
        """
        Verifica se há ordens abertas.
        
        Returns:
            bool: True se há ordens abertas, False caso contrário
        """
        return global_value.order_open
        
    @staticmethod
    def check_order_closed(ido):
        """
        Aguarda até que uma ordem específica seja fechada.
        
        Args:
            ido (int): ID da ordem
            
        Returns:
            int: ID da ordem fechada
        """
        while ido not in global_value.order_closed:
            time.sleep(0.1)

        for pack in global_value.stat:
            if pack[0] == ido:
               print('Ordem Fechada',pack[1])

        return pack[0]
    
    def buy(self, amount, active, action, expirations):
        """
        Realiza uma operação de compra.
        
        Args:
            amount (float): Valor monetário da operação
            active (str): Ativo a ser negociado
            action (str): Tipo de operação ("call" ou "put")
            expirations (int): Tempo de expiração em segundos
            
        Returns:
            tuple: (bool, int) - (Sucesso da operação, ID da ordem ou None)
        """
        self.api.buy_multi_option = {}
        self.api.buy_successful = None
        req_id = "buy"

        try:
            if req_id not in self.api.buy_multi_option:
                self.api.buy_multi_option[req_id] = {"id": None}
            else:
                self.api.buy_multi_option[req_id]["id"] = None
        except Exception as e:
            logging.error(f"Erro ao inicializar buy_multi_option: {e}")
            return False, None

        global_value.order_data = None
        global_value.result = None

        self.api.buyv3(amount, active, action, expirations, req_id)

        start_t = time.time()
        while True:
            if global_value.result is not None and global_value.order_data is not None:
                break
            if time.time() - start_t >= 5:
                if isinstance(global_value.order_data, dict) and "error" in global_value.order_data:
                    logging.error(global_value.order_data["error"])
                else:
                    logging.error("Erro desconhecido ocorreu durante a operação de compra")
                return False, None
            time.sleep(0.1)

        return global_value.result, global_value.order_data.get("id", None)

    def check_win(self, id_number):
        """
        Verifica o resultado de uma operação.
        
        Args:
            id_number (int): ID da ordem a ser verificada
            
        Returns:
            tuple: (float, str) - (Lucro/Prejuízo, Status da operação)
                Status pode ser: "ganhou", "perdeu" ou "desconhecido"
        """
        start_t = time.time()
        order_info = None

        while True:
            try:
                order_info = self.get_async_order(id_number)
                if order_info and "id" in order_info and order_info["id"] is not None:
                    break
            except:
                pass

            if time.time() - start_t >= 120:
                logging.error("Tempo esgotado: Não foi possível recuperar informações da ordem a tempo.")
                return None, "desconhecido"

            time.sleep(0.1)

        if order_info and "profit" in order_info:
            status = "ganhou" if order_info["profit"] > 0 else "perdeu"
            return order_info["profit"], status
        else:
            logging.error("Informações da ordem inválidas recuperadas.")
            return None, "desconhecido"

    @staticmethod
    def last_time(timestamp, period):
        """
        Calcula o timestamp do início do período atual.
        
        Args:
            timestamp (int): Timestamp em segundos
            period (int): Período em segundos
            
        Returns:
            int: Timestamp do início do período
        """
        timestamp_arredondado = (timestamp // period) * period
        return int(timestamp_arredondado)

    def get_candles(self, active, period, start_time=None, count=6000, count_request=1):
        """
        Obtém dados históricos de velas (candles) para um ativo.
        
        Args:
            active (str): Código do ativo (ex: "EURUSD")
            period (int): Período de cada vela em segundos
            start_time (int, optional): Timestamp final para a última vela
            count (int): Número de velas por requisição (max: 9000)
            count_request (int): Número de requisições para dados históricos
            
        Returns:
            pandas.DataFrame: DataFrame com os dados das velas, contendo:
                - time: Timestamp da vela
                - open: Preço de abertura
                - high: Preço máximo
                - low: Preço mínimo
                - close: Preço de fechamento
                - volume: Volume negociado
        """
        try:
            if start_time is None:
                time_sync = self.get_server_timestamp()
                time_red = self.last_time(time_sync, period)
            else:
                time_red = start_time
                time_sync = self.get_server_timestamp()

            all_candles = []

            for _ in range(count_request):
                self.api.history_data = None

                while True:
                    logging.info("Entrou no loop While em GetCandles")
                    try:
                        self.api.getcandles(active, 30, count, time_red)

                        for i in range(1, 100):
                            if self.api.history_data is None:
                                time.sleep(0.1)
                            if i == 99:
                                break

                        if self.api.history_data is not None:
                            all_candles.extend(self.api.history_data)
                            break

                    except Exception as e:
                        logging.error(e)

                all_candles = sorted(all_candles, key=lambda x: x["time"])

                if all_candles:
                    time_red = all_candles[0]["time"]

            df_candles = pd.DataFrame(all_candles)

            df_candles = df_candles.sort_values(by='time').reset_index(drop=True)
            df_candles['time'] = pd.to_datetime(df_candles['time'], unit='s')
            df_candles.set_index('time', inplace=True)
            df_candles.index = df_candles.index.floor('1s')

            df_resampled = df_candles['price'].resample(f'{period}s').ohlc()

            df_resampled.reset_index(inplace=True)

            print("FINALIZADO!!!")

            return df_resampled
        except:
            print("No except")
            return None

    @staticmethod
    def process_data_history(data, period):
        """
        Este método recebe dados históricos, converte-os em um DataFrame do pandas, arredonda os tempos para o minuto mais próximo,
        e calcula os valores OHLC (Abertura, Máxima, Mínima, Fechamento) para cada minuto. Em seguida, converte o resultado em um dicionário
        e o retorna.

        :param dict data: Dados históricos que incluem marcas de tempo e preços.
        :param int period: Período em minutos
        :return: Um dicionário que contém os valores OHLC agrupados por minutos arredondados.
        """
        df = pd.DataFrame(data['history'], columns=['timestamp', 'price'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
        df['minute_rounded'] = df['datetime'].dt.floor(f'{period / 60}min')

        ohlcv = df.groupby('minute_rounded').agg(
            open=('price', 'first'),
            high=('price', 'max'),
            low=('price', 'min'),
            close=('price', 'last')
        ).reset_index()

        ohlcv['time'] = ohlcv['minute_rounded'].apply(lambda x: int(x.timestamp()))
        ohlcv = ohlcv.drop(columns='minute_rounded')

        ohlcv = ohlcv.iloc[:-1]

        ohlcv_dict = ohlcv.to_dict(orient='records')

        return ohlcv_dict

    @staticmethod
    def process_candle(candle_data, period):
        """
        Resumo: Este método estático do Python processa dados de velas financeiras.
        Realiza operações de limpeza e organização usando pandas, incluindo ordenação por tempo,
        remoção de duplicatas e reindexação. Verifica se as diferenças de tempo entre entradas
        consecutivas são iguais ao período especificado.

        :param list candle_data: Dados das velas a processar.
        :param int period: Período de tempo entre as velas em segundos.
        :return: DataFrame processado com os dados das velas.
        """
        data_df = pd.DataFrame(candle_data)
        data_df.sort_values(by='time', ascending=True, inplace=True)
        data_df.drop_duplicates(subset='time', keep="first", inplace=True)
        data_df.reset_index(drop=True, inplace=True)
        data_df.ffill(inplace=True)

        diferencas = data_df['time'].diff()
        diff = (diferencas[1:] == period).all()
        return data_df, diff

    def change_symbol(self, active, period):
        return self.api.change_symbol(active, period)

    def sync_datetime(self):
        return self.api.synced_datetime
