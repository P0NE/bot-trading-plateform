import time
import numpy as np
from binance.client import Client
# from twilio.rest import Client as TwilioClient
from .models import Trade
from django.conf import settings
from .binance_service import place_buy_order, place_sell_order, get_current_price

# Initialiser les clients Binance et Twilio
binance_client = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)
binance_client.API_URL = settings.BINANCE_API_BASE_URL  # Utiliser le testnet ou l'API de production
# twilio_client = TwilioClient(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)

# Fonction pour envoyer des notifications via SMS
# def send_trade_notification(message):
#     twilio_client.messages.create(
#         body=message,
#         from_='+1234567890',  # Numéro Twilio
#         to='+0987654321'  # Ton numéro
#     )

# Fonction pour calculer les bandes de Bollinger
def calculate_bollinger_bands(symbol, period=20, std_dev=2):
    klines = binance_client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY, limit=period)
    close_prices = np.array([float(kline[4]) for kline in klines])
    sma = np.mean(close_prices)
    std = np.std(close_prices)
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    return lower_band, upper_band

# Fonction pour calculer le RSI
def calculate_rsi(symbol, period=14):
    klines = binance_client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY, limit=period)
    close_prices = [float(kline[4]) for kline in klines]
    deltas = np.diff(close_prices)
    gains = deltas[deltas > 0]
    losses = -deltas[deltas < 0]

    average_gain = gains.mean() if len(gains) > 0 else 0
    average_loss = losses.mean() if len(losses) > 0 else 0

    if average_loss == 0:  # Pour éviter la division par zéro
        return 100
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_grid_levels(volatility, base_levels=5, max_levels=10, min_levels=3):
    """
    Calculer dynamiquement le nombre de niveaux de grille en fonction de la volatilité du marché.
    
    :param volatility: Volatilité actuelle (mesurée, par exemple, par l'écart-type du prix).
    :param base_levels: Le nombre de niveaux de grille de base.
    :param max_levels: Nombre maximal de niveaux de grille.
    :param min_levels: Nombre minimal de niveaux de grille.
    :return: Le nombre calculé de niveaux de grille.
    """
    if volatility > 0.03:  # Forte volatilité
        return max(min_levels, base_levels - 2)  # Réduire le nombre de niveaux
    elif volatility < 0.01:  # Faible volatilité
        return min(max_levels, base_levels + 3)  # Augmenter le nombre de niveaux
    else:  # Volatilité moyenne
        return base_levels  # Garder le nombre de niveaux de base

def calculate_grid_step(min_price, max_price, grid_levels):
    """
    Calculer le pas de la grille (grid step), c'est-à-dire l'écart entre chaque niveau de grille.
    
    :param min_price: Le prix minimum dans la grille.
    :param max_price: Le prix maximum dans la grille.
    :param grid_levels: Le nombre de niveaux dans la grille.
    :return: Le pas de la grille, c'est-à-dire la différence entre chaque niveau de grille.
    """
    # Calcul du step en divisant la plage de prix par le nombre de niveaux - 1
    return (max_price - min_price) / (grid_levels - 1)

def calculate_order_size(total_capital, grid_levels):
    """
    Calculer la taille de chaque ordre en fonction du capital total disponible et du nombre de niveaux de grille.

    :param total_capital: Le capital total que tu souhaites allouer au bot (par exemple, 1 BTC).
    :param grid_levels: Le nombre total de niveaux dans la grille.
    :return: La taille de chaque ordre à chaque niveau.
    """
    # Diviser le capital total par le nombre de niveaux pour obtenir la taille de chaque ordre
    return total_capital / grid_levels

# Fonction pour calculer le trailing stop-loss
def trailing_stop_loss(current_price, trailing_percentage, last_high):
    if current_price > last_high:
        last_high = current_price
    stop_loss_price = last_high * (1 - trailing_percentage / 100)
    return stop_loss_price, last_high

# Fonction pour recalculer les paramètres de la grille
def recalculate_grid_parameters(symbol):
    min_price, max_price = calculate_bollinger_bands(symbol)
    klines = binance_client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY, limit=20)
    close_prices = np.array([float(kline[4]) for kline in klines])
    volatility = np.std(close_prices) / np.mean(close_prices)

    grid_levels = calculate_grid_levels(volatility)
    grid_step = calculate_grid_step(min_price, max_price, grid_levels)
    total_capital = 1  # Exemple de 1 BTC
    order_size = calculate_order_size(total_capital, grid_levels)

    return grid_levels, grid_step, order_size, min_price, max_price

# Fonction principale pour le trading multi-actifs
def run_dynamic_grid_trading_bot():
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Multi-cryptomonnaies
    last_highs = {symbol: 0 for symbol in symbols}
    trailing_percentage = 5  # Pour trailing stop-loss

    recalculation_interval = 6 * 60 * 60  # Toutes les 6 heures
    last_recalculation_time = time.time() - recalculation_interval

    while True:
        try:
            # Recalculer les paramètres toutes les 6 heures
            if time.time() - last_recalculation_time >= recalculation_interval:
                for symbol in symbols:
                    grid_levels_prices, grid_step, order_size, min_price, max_price = recalculate_grid_parameters(symbol)
                    last_recalculation_time = time.time()

            # Pour chaque cryptomonnaie
            for symbol in symbols:
                current_price = get_current_price(symbol)
                if current_price is None:
                    continue

                # Trailing stop-loss dynamique
                stop_loss_price, last_highs[symbol] = trailing_stop_loss(current_price, trailing_percentage, last_highs[symbol])

                # RSI pour ajuster la stratégie
                rsi = calculate_rsi(symbol)
                if rsi < 30:  # Survente
                    print(f"RSI à {rsi} pour {symbol}, marché survendu.")
                elif rsi > 70:  # Surachat
                    print(f"RSI à {rsi} pour {symbol}, marché suracheté.")

                # Vérifier les niveaux de grille et passer les ordres
                for level in grid_levels_prices:
                    if current_price <= level:  # Achat
                        place_buy_order(symbol, order_size, level)
                        send_trade_notification(f"Achat exécuté à {level} USDT pour {symbol}")
                    elif current_price >= level:  # Vente
                        place_sell_order(symbol, order_size, level)
                        send_trade_notification(f"Vente exécutée à {level} USDT pour {symbol}")

            time.sleep(10)

        except Exception as e:
            print(f"Erreur dans le bot : {e}")

if __name__ == "__main__":
    run_dynamic_grid_trading_bot()
