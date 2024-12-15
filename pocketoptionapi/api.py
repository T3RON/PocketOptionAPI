"""
Interface principal para comunicação com a API da PocketOption.
"""
import asyncio
import datetime
import time
import json
import logging
import threading
import requests
import ssl
import atexit
from collections import deque
from pocketoptionapi.ws.client import WebsocketClient
from pocketoptionapi.ws.channels.get_balances import *
from pocketoptionapi.ws.channels.ssid import Ssid
from pocketoptionapi.ws.channels.candles import GetCandles
from pocketoptionapi.ws.channels.buyv3 import *
from pocketoptionapi.ws.objects.timesync import TimeSync
from pocketoptionapi.ws.objects.candles import Candles
import pocketoptionapi.global_value as global_value
from pocketoptionapi.ws.channels.change_symbol import ChangeSymbol
from collections import defaultdict
from pocketoptionapi.ws.objects.time_sync import TimeSynchronizer

def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))

class PocketOptionAPI(object):
    """Classe para comunicação com a API da Pocket Option."""

    socket_option_opened = {}
    time_sync = TimeSync()
    sync = TimeSynchronizer()
    timesync = None
    candles = Candles()
    api_option_init_all_result = []
    api_option_init_all_result_v2 = []
    underlying_list_data = None
    position_changed = None
    instrument_quites_generated_data = nested_dict(2, dict)
    instrument_quotes_generated_raw_data = nested_dict(2, dict)
    instrument_quites_generated_timestamp = nested_dict(2, dict)
    strike_list = None
    leaderboard_deals_client = None
    order_async = None
    instruments = None
    financial_information = None
    buy_id = None
    buy_order_id = None
    traders_mood = {}  # obtém porcentagem alta (put)
    order_data = None
    positions = None
    position = None
    deferred_orders = None
    position_history = None
    position_history_v2 = None
    available_leverages = None
    order_canceled = None
    close_position_data = None
    overnight_fee = None
    digital_option_placed_id = None
    live_deal_data = nested_dict(3, deque)
    subscribe_commission_changed_data = nested_dict(2, dict)
    real_time_candles = nested_dict(3, dict)
    real_time_candles_maxdict_table = nested_dict(2, dict)
    candle_generated_check = nested_dict(2, dict)
    candle_generated_all_size_check = nested_dict(1, dict)
    api_game_getoptions_result = None
    sold_options_respond = None
    tpsl_changed_respond = None
    auto_margin_call_changed_respond = None
    top_assets_updated_data = {}
    get_options_v2_data = None
    buy_multi_result = None
    buy_multi_option = {}
    result = None
    training_balance_reset_request = None
    balances_raw = None
    user_profile_client = None
    leaderboard_userinfo_deals_client = None
    users_availability = None
    history_data = None
    historyNew = None
    server_timestamp = None
    sync_datetime = None

    def __init__(self, proxies=None):
        """
        :param dict proxies: (opcional) Os proxies para requisições http.
        """
        self.websocket_client = None
        self.websocket_thread = None
        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False
        self.proxies = proxies
        # usado para determinar se uma ordem de compra foi definida ou falhou
        # Se for None, não houve ordem de compra ainda ou acabou de ser enviada
        # Se for False, a última falhou
        # Se for True, a última ordem de compra foi bem-sucedida
        self.buy_successful = None
        self.loop = asyncio.get_event_loop()
        self.websocket_client = WebsocketClient(self)

    @property
    def websocket(self):
        """Propriedade para obter websocket.

        :returns: A instância de :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client
    
    def GetPayoutData(self):
        return global_value.PayoutData

    def send_websocket_request(self, name, msg, request_id="", no_force_send=True):
        """Envia requisição websocket para o servidor da Pocket Option.

        :param no_force_send: Se não deve forçar o envio
        :param request_id: ID da requisição
        :param str name: Nome da requisição websocket
        :param dict msg: Mensagem da requisição websocket
        """
        logger = logging.getLogger(__name__)

        data = f'42{json.dumps(msg)}'

        while (global_value.ssl_Mutual_exclusion or global_value.ssl_Mutual_exclusion_write) and no_force_send:
            pass
        global_value.ssl_Mutual_exclusion_write = True

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.websocket.send_message(data))

        logger.debug(data)
        global_value.ssl_Mutual_exclusion_write = False

    def start_websocket(self):
        global_value.websocket_is_connected = False
        global_value.check_websocket_if_error = False
        global_value.websocket_error_reason = None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.websocket.connect())
        loop.run_forever()

        while True:
            try:
                if global_value.check_websocket_if_error:
                    return False, global_value.websocket_error_reason
                if global_value.websocket_is_connected is False:
                    return False, "Conexão websocket fechada."
                elif global_value.websocket_is_connected is True:
                    return True, None
            except:
                pass

    def connect(self):
        """Método para conexão com a API da Pocket Option."""

        global_value.ssl_Mutual_exclusion = False
        global_value.ssl_Mutual_exclusion_write = False

        check_websocket, websocket_reason = self.start_websocket()

        if not check_websocket:
            return check_websocket, websocket_reason

        self.time_sync.server_timestamps = None
        while True:
            try:
                if self.time_sync.server_timestamps is not None:
                    break
            except:
                pass
        return True, None

    async def close(self, error=None):
        await self.websocket.on_close(error)
        self.websocket_thread.join()

    def websocket_alive(self):
        return self.websocket_thread.is_alive()

    @property
    def get_balances(self):
        """Propriedade para obter o recurso http getprofile da Pocket Option.

        :returns: A instância de :class:`Login
            <pocketoptionapi.http.getprofile.Getprofile>`.
        """
        return Get_Balances(self)

    @property
    def buyv3(self):
        return Buyv3(self)

    @property
    def getcandles(self):
        """Propriedade para obter o canal websocket de velas da Pocket Option.

        :returns: A instância de :class:`GetCandles
            <pocketoptionapi.ws.channels.candles.GetCandles>`.
        """
        return GetCandles(self)

    @property
    def change_symbol(self):
        """Propriedade para obter o canal websocket change_symbol da Pocket Option.

        :returns: A instância de :class:`ChangeSymbol
            <pocketoptionapi.ws.channels.change_symbol.ChangeSymbol>`.
        """
        return ChangeSymbol(self)

    @property
    def synced_datetime(self):
        try:
            if self.time_sync is not None:
                self.sync.synchronize(self.time_sync.server_timestamp)
                self.sync_datetime = self.sync.get_synced_datetime()
            else:
                logging.error("timesync não está definido")
                self.sync_datetime = None
        except Exception as e:
            logging.error(e)
            self.sync_datetime = None

        return self.sync_datetime
