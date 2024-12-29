# PocketOption API

Uma API Python robusta e fácil de usar para integração com a PocketOption.

## 📦 Instalação

Você pode instalar a API de duas maneiras:

### Via pip (diretamente do GitHub):
```bash
pip install git+https://github.com/AdminhuDev/pocketoptionapi.git
```

### Instalação local (para desenvolvimento):
```bash
git clone https://github.com/AdminhuDev/pocketoptionapi.git
cd pocketoptionapi
pip install -e .
```

## 🚀 Uso Rápido

```python
from pocketoptionapi import PocketOption

# Inicializar a API
api = PocketOption(email="seu_email", password="sua_senha")

# Fazer login
api.connect()

# Verificar saldo
saldo = api.get_balance()
print(f"Saldo atual: {saldo}")

# Fazer uma operação
api.buy(
    price=10,           # Valor da operação
    asset="EURUSD",     # Ativo
    direction="call",   # Direção (call/put)
    duration=1          # Duração em minutos
)
```

## 🔧 Funcionalidades

- ✅ Login e autenticação segura
- ✅ Operações de compra e venda
- ✅ Consulta de saldo
- ✅ Histórico de operações
- ✅ Dados em tempo real
- ✅ Suporte a múltiplos ativos
- ✅ Gerenciamento de expiração
- ✅ WebSocket para dados em tempo real

## 📚 Documentação Detalhada

### Classe PocketOption

#### Métodos Principais:

```python
def connect() -> bool:
    """Conecta à PocketOption e retorna True se bem sucedido"""

def get_balance() -> float:
    """Retorna o saldo atual da conta"""

def buy(price: float, asset: str, direction: str, duration: int) -> dict:
    """
    Realiza uma operação de compra
    
    Args:
        price: Valor da operação
        asset: Nome do ativo (ex: "EURUSD")
        direction: Direção ("call" ou "put")
        duration: Duração em minutos
    
    Returns:
        dict: Informações da operação
    """

def get_candles(asset: str, interval: int = 60) -> list:
    """
    Obtém dados históricos de candles
    
    Args:
        asset: Nome do ativo
        interval: Intervalo em segundos
    
    Returns:
        list: Lista de candles
    """
```

### Classe PocketOptionAPI (Versão Estável)

Versão mais estável e robusta da API, com funcionalidades adicionais:

```python
from pocketoptionapi import PocketOptionAPI

api = PocketOptionAPI(email="seu_email", password="sua_senha")
```

## ⚙️ Configuração

A API utiliza as seguintes dependências principais:
- websocket-client>=1.6.1
- requests>=2.31.0
- python-dateutil>=2.8.2
- pandas>=2.1.3

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, siga estes passos:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: nova funcionalidade'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## ⚠️ Aviso Legal

Este projeto não é afiliado oficialmente à PocketOption. Use por sua conta e risco. 