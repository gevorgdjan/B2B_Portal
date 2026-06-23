from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderCreateSerializer


class OrderAPIView(generics.ListCreateAPIView):
    """
    Контроллер для работы с заказами текущего авторизованного пользователя.

    Предоставляет методы:
    - GET: Возвращает список заказов клиента. Решает проблему N+1 запроса
      за счет использования prefetch_related для товаров и select_related для клиента.
    - POST: Создает новый заказ. Перенаправляет данные в OrderCreateSerializer.
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer

        from rest_framework.serializers import ModelSerializer

        class SimpleOrderSerializer(ModelSerializer):
            class Meta:
                model = Order
                fields = '__all__'

        return SimpleOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user) \
            .prefetch_related('items__product') \
            .select_related('client')