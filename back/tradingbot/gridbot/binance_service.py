from binance.client import Client
from django.conf import settings

# Utiliser le testnet de Binance
client = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)
client.API_URL = settings.BINANCE_API_BASE_URL  # Configurer l'URL pour le testnet

# Fonction pour passer un ordre d'achat (testnet)
def place_buy_order(symbol, quantity, price):
    try:
        order = client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price=str(price)
        )
        return order
    except Exception as e:
        print(f"Erreur lors de la création de l'ordre d'achat : {e}")
        return None

# Fonction pour passer un ordre de vente (testnet)
def place_sell_order(symbol, quantity, price):
    try:
        order = client.order_limit_sell(
            symbol=symbol,
            quantity=quantity,
            price=str(price)
        )
        return order
    except Exception as e:
        print(f"Erreur lors de la création de l'ordre de vente : {e}")
        return None

# Fonction pour obtenir les prix actuels (testnet)
def get_current_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])
    except Exception as e:
        print(f"Erreur lors de la récupération du prix : {e}")
        return None
