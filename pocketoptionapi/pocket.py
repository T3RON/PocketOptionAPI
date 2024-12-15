"""
Autor: AdminhuDev
"""
from pocketoptionapi.backend.ws.client import WebSocketClient
from pocketoptionapi.backend.ws.chat import WebSocketClientChat
import threading
import ssl
import decimal
import json
import urllib
import websocket
import logging
import pause
from websocket._exceptions import WebSocketException

class PocketOptionApi:
    def __init__(self, init_msg) -> None:
        self.ws_url = "wss://api-fin.po.market/socket.io/?EIO=4&transport=websocket"
        self.token = "TEST_TOKEN"
        self.connected_event = threading.Event()
        self.client = WebSocketClient(self.ws_url)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.init_msg = init_msg
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        self.websocket_client = WebSocketClient(self.ws_url, pocket_api_instance=self)

        # Cria manipulador de arquivo e adiciona ao logger
        file_handler = logging.FileHandler('pocket.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f"Iniciando API Pocket com token: {self.token}")

        self.websocket_client_chat = WebSocketClientChat(url="wss://chat-po.site/cabinet-client/socket.io/?EIO=4&transport=websocket")
        self.websocket_client_chat.run()

        self.logger.info("Enviando websocket de chat")

        self.websocket_client.ws.run_forever()

    def auto_ping(self):
        self.logger.info("Iniciando thread de auto ping")
        pause.seconds(5)
        while True:
            try:
                if self.websocket_client.ws.sock and self.websocket_client.ws.sock.connected:  # Verifica se o socket está conectado
                    self.ping()
                else:
                    self.logger.warning("WebSocket não está conectado. Tentando reconectar.")
                    # Tenta reconexão
                    if self.connect():
                        self.logger.info("Reconectado com sucesso.")
                    else:
                        self.logger.warning("Tentativa de reconexão falhou.")
                    try:
                        self.ping()
                        self.logger.info("Ping enviado com sucesso!")
                    except Exception as e:
                        self.logger.error(f"Ocorreu um erro ao tentar enviar ping: {e}")
            except Exception as e:  # Captura exceções e registra
                self.logger.error(f"Ocorreu um erro ao enviar ping ou tentar reconectar: {e}")
                try:
                    self.logger.warning("Tentando novamente...")
                    v1 = self.connect()
                    if v1:
                        self.logger.info("Conexão completada!, enviando ping...")
                        self.ping()
                    else:
                        self.logger.error("Conexão não foi estabelecida")
                except Exception as e:
                    self.logger.error(f"Ocorreu um erro ao tentar novamente: {e}")

    def connect(self):
        self.logger.info("Tentando conectar...")

        self.websocket_client_chat.ws.send("40")
        data = r"""42["user_init",{"id":27658142,"secret":"8ed9be7299c3aa6363e57ae5a4e52b7a"}]"""
        self.websocket_client_chat.ws.send(data)
        try:
            self.websocket_thread = threading.Thread(target=self.websocket_client.ws.run_forever, kwargs={
                'sslopt': {
                    "check_hostname": False,
                    "cert_reqs": ssl.CERT_NONE,
                    "ca_certs": "cacert.pem"
                },
                "ping_interval": 0,
                'skip_utf8_validation': True,
                "origin": "https://pocketoption.com",
                # "http_proxy_host": '127.0.0.1', "http_proxy_port": 8890
            })

            self.websocket_thread.daemon = True
            self.websocket_thread.start()

            self.logger.info("Conexão bem sucedida.")

            self.send_websocket_request(msg="40")
            self.send_websocket_request(self.init_msg)
        except Exception as e:
            print(f"Indo para exceção.... erro: {e}")
            self.logger.error(f"Conexão falhou com exceção: {e}")

    def send_websocket_request(self, msg):
        """Envia requisição websocket para o servidor PocketOption.
        :param dict msg: A mensagem de requisição websocket.
        """
        self.logger.info(f"Enviando requisição websocket: {msg}")
        def default(obj):
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            raise TypeError

        data = json.dumps(msg, default=default)

        try:
            self.logger.info("Requisição enviada com sucesso.")
            self.websocket_client.ws.send(bytearray(urllib.parse.quote(data).encode('utf-8')), opcode=websocket.ABNF.OPCODE_BINARY)
            return True
        except Exception as e:
            self.logger.error(f"Falha ao enviar requisição com exceção: {e}")
            # Considere adicionar qualquer código necessário de tratamento de exceção aqui
            try:
                self.websocket_client.ws.send(bytearray(urllib.parse.quote(data).encode('utf-8')), opcode=websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                self.logger.warning(f"Não foi possível reconectar: {e}")
    
    def _login(self, init_msg):
        self.logger.info("Tentando fazer login...")

        self.websocket_thread = threading.Thread(target=self.websocket_client.ws.run_forever, kwargs={
                'sslopt': {
                    "check_hostname": False,
                    "cert_reqs": ssl.CERT_NONE,
                    "ca_certs": "cacert.pem"
                },
                "ping_interval": 0,
                'skip_utf8_validation': True,
                "origin": "https://pocketoption.com",
                # "http_proxy_host": '127.0.0.1', "http_proxy_port": 8890
            })

        self.websocket_thread.daemon = True
        self.websocket_thread.start()

        self.logger.info("Thread de login inicializada com sucesso!")

        # self.send_websocket_request(msg=init_msg)
        self.websocket_client.ws.send(init_msg)

        self.logger.info(f"Mensagem foi enviada com sucesso para fazer seu login!, mensagem: {init_msg}")

        try:
            self.websocket_client.ws.run_forever()
        except WebSocketException as e:
            self.logger.error(f"Ocorreu um erro com websocket: {e}")
            # self.send_websocket_request(msg=init_msg)
            try:
                self.websocket_client.ws.run_forever()
                self.send_websocket_request(msg=init_msg)
            except Exception as e:
                self.logger.error(f"Nova tentativa falhou, pulando... erro: {e}")
                # self.send_websocket_request(msg=init_msg)

    @property
    def ping(self):
        self.send_websocket_request(msg="3")
        self.logger.info("Enviou uma requisição de ping")
        return True
