from django.urls import path
from . import views

urlpatterns = [
    # Route pour créer un ordre d'achat
    path('create_buy_order/', views.create_buy_order, name='create_buy_order'),
    
    # Route pour créer un ordre de vente
    path('create_sell_order/', views.create_sell_order, name='create_sell_order'),
]
