"""
Cliente WebSocket para comunicação com a PocketOption.
"""
import asyncio
from datetime import datetime, timedelta, timezone
import websockets
import json
import logging
import ssl
import pocketoptionapi.constants as OP_code
import pocketoptionapi.global_value as global_value
from pocketoptionapi.constants import REGION
from pocketoptionapi.ws.objects.timesync import TimeSync
from pocketoptionapi.ws.objects.time_sync import TimeSynchronizer

logger = logging.getLogger(__name__)

timesync = TimeSync()
sync = TimeSynchronizer()

async def on_open():
    """Método para processar a abertura do websocket."""
    print("CONEXÃO BEM SUCEDIDA")
    logger.debug("Cliente websocket conectado.")
    global_value.websocket_is_connected = True

async def send_ping(ws):
    while global_value.websocket_is_connected is False:
        await asyncio.sleep(0.1)
    while True:
        try:
            await ws.send('42["ps"]')
            await asyncio.sleep(20)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed during ping, attempting reconnect...")
            break
        except Exception as e:
            logger.error(f"Error during ping: {e}")
            await asyncio.sleep(5)

class WebsocketClient(object):
    def __init__(self, api) -> None:
        self.updateHistoryNew = None
        self.updateStream = None
        self.history_data_ready = None
        self.successCloseOrder = False
        self.api = api
        self.message = None
        self.url = None
        self.ssid = global_value.SSID
        self.websocket = None
        self.region = REGION()
        self.loop = asyncio.get_event_loop()
        self.wait_second_message = False
        self._updateClosedDeals = False
        self.reconnect_delay = 5  # Initial delay in seconds
        self.max_reconnect_delay = 60  # Maximum delay in seconds

    async def websocket_listener(self, ws):
        try:
            async for message in ws:
                await self.on_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed, attempting reconnect...")
            global_value.websocket_is_connected = False
        except Exception as e:
            logger.error(f"Error in websocket listener: {e}")
            global_value.websocket_is_connected = False

    async def connect(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        while not global_value.websocket_is_connected:
            for url in self.region.get_regions(True):
                try:
                    headers = {
                        "Origin": "https://pocketoption.com",
                        "Cache-Control": "no-cache",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    }
                    
                    async with websockets.connect(
                            url,
                            ssl=ssl_context,
                            extra_headers=headers
                    ) as ws:
                        self.websocket = ws
                        self.url = url
                        global_value.websocket_is_connected = True
                        self.reconnect_delay = 5  # Reset delay on successful connection

                        tasks = [
                            self.websocket_listener(ws),
                            self.send_message(self.message),
                            send_ping(ws)
                        ]
                        
                        await asyncio.gather(*tasks)

                except Exception as e:
                    logger.error(f"Connection error: {e}")
                    global_value.websocket_is_connected = False
                    await asyncio.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

            await asyncio.sleep(1)

        return True

    async def send_message(self, message):
        while global_value.websocket_is_connected is False:
            await asyncio.sleep(0.1)

        self.message = message

        if global_value.websocket_is_connected and message is not None:
            try:
                await self.websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection closed while sending message")
                global_value.websocket_is_connected = False
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                global_value.websocket_is_connected = False
        elif message is not None:
            logger.warning("WebSocket not connected")

    @staticmethod
    def dict_queue_add(self, dict, maxdict, key1, key2, key3, value):
        if key3 in dict[key1][key2]:
            dict[key1][key2][key3] = value
        else:
            while True:
                try:
                    dic_size = len(dict[key1][key2])
                except:
                    dic_size = 0
                if dic_size < maxdict:
                    dict[key1][key2][key3] = value
                    break
                else:
                    del dict[key1][key2][sorted(dict[key1][key2].keys(), reverse=False)[0]]

    async def on_message(self, message):
        """Método para processar mensagens do websocket."""
        logger.debug(message)

        if isinstance(message, bytes):
            message2 = message.decode('utf-8')
            message = message.decode('utf-8')
            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                logger.warning("Failed to decode message as JSON")
                return

            if "balance" in message:
                if "uid" in message:
                    global_value.balance_id = message["uid"]
                global_value.balance = message["balance"]
                global_value.balance_type = message["isDemo"]

            elif "requestId" in message and message["requestId"] == 'buy':
                global_value.order_data = message

            elif self.wait_second_message and isinstance(message, list):
                self.wait_second_message = False
                self._updateClosedDeals = False

            elif isinstance(message, dict) and self.successCloseOrder:
                self.api.order_async = message
                self.successCloseOrder = False

            elif self.history_data_ready and isinstance(message, dict):
                self.history_data_ready = False
                self.api.history_data = message["data"]

            elif self.updateStream and isinstance(message, list):
                self.updateStream = False
                self.api.time_sync.server_timestamp = message[0][1]

            elif self.updateHistoryNew and isinstance(message, dict):
                self.updateHistoryNew = False
                self.api.historyNew = message
            elif '[[5,"#AAPL","Apple","stock' in message2:
                global_value.PayoutData = message2
            return

        if message.startswith('0') and "sid" in message:
            await self.websocket.send("40")

        elif message == "2":
            await self.websocket.send("3")

        elif "40" and "sid" in message:
            await self.websocket.send(self.ssid)

        elif message.startswith('451-['):
            try:
                json_part = message.split("-", 1)[1]
                message = json.loads(json_part)

                if message[0] == "successauth":
                    await on_open()

                elif message[0] == "successupdateBalance":
                    global_value.balance_updated = True
                elif message[0] == "successopenOrder":
                    global_value.result = True

                elif message[0] == "updateClosedDeals":
                    self._updateClosedDeals = True
                    self.wait_second_message = True
                    await self.websocket.send('42["changeSymbol",{"asset":"AUDNZD_otc","period":60}]')

                elif message[0] == "successcloseOrder":
                    self.successCloseOrder = True
                    self.wait_second_message = True

                elif message[0] == "loadHistoryPeriod":
                    self.history_data_ready = True

                elif message[0] == "updateStream":
                    self.updateStream = True

                elif message[0] == "updateHistoryNew":
                    self.updateHistoryNew = True

            except json.JSONDecodeError:
                logger.warning("Failed to decode JSON message")
            except Exception as e:
                logger.error(f"Error processing message: {e}")

        elif message.startswith("42") and "NotAuthorized" in message:
            logging.error("User not Authorized: Please Change SSID for one valid")
            global_value.ssl_Mutual_exclusion = False
            await self.websocket.close()

    async def on_error(self, error):
        logger.error(error)
        global_value.websocket_error_reason = str(error)
        global_value.check_websocket_if_error = True

    async def on_close(self, error):
        global_value.websocket_is_connected = False