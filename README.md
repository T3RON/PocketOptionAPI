# PocketOptionAPI

API não oficial para a plataforma PocketOption, desenvolvida em Python.

## Instalação

```bash
git clone https://github.com/AdminhuDev/PocketOptionAPI.git
cd PocketOptionAPI
pip install -r requirements.txt
```

## Uso Básico

```python
import time
from pocketoptionapi.stable_api import PocketOption
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

# Configurar sessão
ssid = """42["auth",{"session":"sua_sessao_aqui","isDemo":1,"uid":seu_uid_aqui,"platform":2}]"""
demo = True

# Inicializar API
api = PocketOption(ssid, demo)

# Conectar
connect = api.connect()
print(connect)
time.sleep(10)

# Obter saldo
balance = api.get_balance()
print(balance)
time.sleep(1)

# Obter dados das velas
get_candles = api.get_candles("EURUSD_otc", 100)
print(get_candles)
```

## Funcionalidades

- Conexão WebSocket com a plataforma PocketOption
- Autenticação e gerenciamento de sessão
- Obtenção de dados de mercado em tempo real
- Execução de operações de trading
- Gerenciamento de conta e saldo
- Suporte a contas demo e real

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests.

## Autor

AdminhuDev

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Aviso Legal

Este é um projeto não oficial e não tem nenhuma afiliação com a PocketOption. Use por sua própria conta e risco. 