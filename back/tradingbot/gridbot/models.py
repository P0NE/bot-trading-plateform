from django.db import models
from django.contrib.auth.models import User

class GridConfig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10, default="BTCUSDT")  # Cryptomonnaie (ex: BTCUSDT)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)  # Prix minimum de la grille
    max_price = models.DecimalField(max_digits=10, decimal_places=2)  # Prix maximum de la grille
    grid_step = models.DecimalField(max_digits=10, decimal_places=2)  # Pas entre les niveaux
    grid_levels = models.IntegerField(default=5)  # Nombre de niveaux
    order_size = models.DecimalField(max_digits=10, decimal_places=4)  # Taille des ordres
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création de la grille

class Trade(models.Model):
    grid_config = models.ForeignKey(GridConfig, on_delete=models.CASCADE)
    trade_type = models.CharField(max_length=10)  # 'buy' ou 'sell'
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Prix d'exécution
    quantity = models.DecimalField(max_digits=10, decimal_places=4)  # Quantité échangée
    executed_at = models.DateTimeField(auto_now_add=True)  # Date d'exécution du trade
