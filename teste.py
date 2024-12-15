"""
Autor: AdminhuDev
"""
import time
from pocketoptionapi.stable_api import PocketOption
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')

# Configuração da sessão
ssid="""42["auth",{"session":"9bdissutko91fhkragll3689no","isDemo":1,"uid":89224537,"platform":2}]"""
demo=True
api = PocketOption(ssid,demo)

# Conecta à API
connect=api.connect()
print(connect)
time.sleep(10)

# Obtém o saldo
balance=api.get_balance()
print(balance)
time.sleep(1)

# Obtém os dados das velas
get_candles=api.get_candles("EURUSD_otc",100)
print(get_candles)
