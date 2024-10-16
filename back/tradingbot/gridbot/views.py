from rest_framework import viewsets
from .models import GridConfig, Trade
# from .serializers import GridConfigSerializer, TradeSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .binance_service import place_buy_order, place_sell_order, get_current_price

# class GridConfigViewSet(viewsets.ModelViewSet):
#     queryset = GridConfig.objects.all()
#     serializer_class = GridConfigSerializer

# class TradeViewSet(viewsets.ModelViewSet):
#     queryset = Trade.objects.all()
#     serializer_class = TradeSerializer

@api_view(['POST'])
def create_buy_order(request):
    symbol = request.data.get("symbol", "BTCUSDT")
    quantity = request.data.get("quantity", 0.001)
    price = request.data.get("price", None)

    if not price:
        price = get_current_price(symbol)
    
    order = place_buy_order(symbol, quantity, price)
    if order:
        return Response({"status": "Order created", "order": order})
    else:
        return Response({"status": "Failed to create order"}, status=500)

@api_view(['POST'])
def create_sell_order(request):
    symbol = request.data.get("symbol", "BTCUSDT")
    quantity = request.data.get("quantity", 0.001)
    price = request.data.get("price", None)

    if not price:
        price = get_current_price(symbol)

    order = place_sell_order(symbol, quantity, price)
    if order:
        return Response({"status": "Order created", "order": order})
    else:
        return Response({"status": "Failed to create order"}, status=500)