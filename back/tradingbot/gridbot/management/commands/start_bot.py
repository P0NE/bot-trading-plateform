import threading
import time
from django.core.management.base import BaseCommand
from gridbot.grid_trading_bot import run_dynamic_grid_trading_bot  # Import de ta fonction de bot

class Command(BaseCommand):
    help = 'Démarre le bot de trading'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Lancement du bot de trading...'))

        # Lancer le bot en utilisant threading pour l'exécuter en arrière-plan
        bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        bot_thread.start()

        # Rendre le processus interactif pour maintenir le bot actif
        while True:
            time.sleep(10)

    def run_bot(self):
        # Appeler la fonction qui démarre le bot de grid trading
        run_dynamic_grid_trading_bot()
