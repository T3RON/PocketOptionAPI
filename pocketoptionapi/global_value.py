"""
Autor: AdminhuDev
"""
# Variáveis globais
websocket_is_connected = False
# Tentativa de corrigir ssl.SSLEOFError: EOF ocorreu em violação do protocolo (_ssl.c:2361)
ssl_Mutual_exclusion = False  # mutex leitura/escrita
# Se falso, websocket pode enviar self.websocket.send(data)
# Caso contrário, não pode enviar self.websocket.send(data)
ssl_Mutual_exclusion_write = False  # se thread escrever

SSID = None

check_websocket_if_error = False
websocket_error_reason = None

balance_id = None
balance = None
balance_type = None
balance_updated = None
result = None
order_data = {}
order_open = []
order_closed = []
stat = []
DEMO = None

# Para obter os dados de pagamento para os diferentes pares
PayoutData = None