from binance.client import Client
from django.conf import settings

# Utiliser le testnet de Binance
client = Client(settings.BINANCE_API_TEST_KEY, settings.BINANCE_API_TEST_SECRET)
client.API_URL = settings.BINANCE_API_BASE_URL  # Configurer l'URL pour le testnet

def get_price_precision(symbol):
    info = client.get_symbol_info(symbol)
    for filt in info['filters']:
        if filt['filterType'] == 'PRICE_FILTER':
            return int(filt['tickSize'].find('1') - 2)

def round_price(symbol, price):
    precision = get_price_precision(symbol)
    return round(price, precision)

def get_quantity_limits(symbol):
    info = client.get_symbol_info(symbol)
    
    for filt in info['filters']:
        if filt['filterType'] == 'LOT_SIZE':
            min_qty = float(filt['minQty'])
            max_qty = float(filt['maxQty'])
            step_size = float(filt['stepSize'])
            return min_qty, max_qty, step_size
    raise ValueError(f"Le filtre LOT_SIZE n'a pas été trouvé pour la paire {symbol}")

def get_price_limits(symbol):
    info = client.get_symbol_info(symbol)
    
    for filt in info['filters']:
        if filt['filterType'] == 'PRICE_FILTER':
            min_price = float(filt['minPrice'])
            max_price = float(filt['maxPrice'])
            tick_size = float(filt['tickSize'])
            return min_price, max_price, tick_size
    raise ValueError(f"Le filtre PRICE_FILTER n'a pas été trouvé pour la paire {symbol}")

def validate_and_adjust_quantity(symbol, quantity):
    min_qty, max_qty, step_size = get_quantity_limits(symbol)

    if quantity < min_qty or quantity > max_qty:
        raise ValueError(f"La quantité {quantity} est en dehors des limites autorisées ({min_qty}, {max_qty}).")

    rounded_quantity = round(quantity / step_size) * step_size
    return rounded_quantity

def validate_and_adjust_price(symbol, price):
    min_price, max_price, tick_size = get_price_limits(symbol)

    if price < min_price or price > max_price:
        raise ValueError(f"Le prix {price} est en dehors des limites autorisées ({min_price}, {max_price}).")

    rounded_price = round(price / tick_size) * tick_size
    return rounded_price

# Fonction pour passer un ordre d'achat (testnet)
def place_buy_order(symbol, quantity, price):
    rounded_price = round_price(symbol, price)
    try:
        validated_quantity = validate_and_adjust_quantity(symbol, quantity)
        # Valider que le prix respecte les limites
        validated_price = validate_and_adjust_price(symbol, price)
        order = client.order_limit_buy(
            symbol=symbol,
            quantity=validated_quantity,
            price=str(rounded_price)
        )
        return order
    except Exception as e:
        print(f"Erreur lors de la création de l'ordre d'achat : {e}")
        return None

# Fonction pour passer un ordre de vente (testnet)
def place_sell_order(symbol, quantity, price):
    rounded_price = round_price(symbol, price)
    try:
        validated_quantity = validate_and_adjust_quantity(symbol, quantity)
        # Valider que le prix respecte les limites
        validated_price = validate_and_adjust_price(symbol, price)
        order = client.order_limit_sell(
            symbol=symbol,
            quantity=validated_quantity,
            price=str(rounded_price)
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
