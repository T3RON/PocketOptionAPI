# PocketOptionAPI

API não oficial para a plataforma PocketOption, desenvolvida em Python.

## Características

- ✨ Interface Python moderna e fácil de usar
- 🔄 Conexão WebSocket em tempo real
- 📊 Dados de mercado em tempo real
- 💰 Suporte a contas demo e real
- 📈 Operações de trading automatizadas
- 🔐 Gerenciamento seguro de sessão

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
demo = True  # True para conta demo, False para conta real

# Inicializar API
api = PocketOption(ssid, demo)

# Conectar
connect = api.connect()
print(connect)
time.sleep(10)

# Obter saldo
balance = api.get_balance()
print(f"Saldo atual: {balance}")

# Obter dados das velas
candles = api.get_candles("EURUSD_otc", 60)  # Velas de 1 minuto
print("Últimas velas:", candles)

# Realizar uma operação
amount = 1.0  # Valor em dólares
active = "EURUSD_otc"  # Ativo
action = "call"  # "call" para compra, "put" para venda
expiration = 60  # Tempo de expiração em segundos

result, order_id = api.buy(amount, active, action, expiration)
if result:
    print(f"Ordem {order_id} executada com sucesso!")
    
    # Verificar resultado
    profit, status = api.check_win(order_id)
    print(f"Resultado: {status} (Lucro/Prejuízo: {profit})")
```

## Funcionalidades Detalhadas

### Conexão e Autenticação
- Conexão WebSocket em tempo real
- Suporte a contas demo e real
- Gerenciamento automático de reconexão

### Trading
- Operações de compra e venda
- Suporte a múltiplos ativos
- Verificação de resultados
- Gestão de ordens em tempo real

### Dados de Mercado
- Cotações em tempo real
- Dados históricos de velas
- Indicadores técnicos
- Análise de tendências

### Gerenciamento de Conta
- Consulta de saldo
- Histórico de operações
- Status da conta
- Gestão de risco

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Aviso Legal

Este é um projeto não oficial e não tem nenhuma afiliação com a PocketOption. Use por sua própria conta e risco. O autor não se responsabiliza por perdas financeiras ou problemas técnicos decorrentes do uso desta API. 