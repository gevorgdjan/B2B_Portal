from django.db import transaction
from rest_framework import serializers

from catalog.models import Product

from .models import Order, OrderItem


class OrderItemCreateSerializer(serializers.Serializer):
    """DTO для получения строки заказа от клиента."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    """
    Сериализатор для валидации и создания заказа с вложенными товарами.

    Выполняет следующие действия:
    1. Проверяет наличие всех запрошенных товаров на складе.
    2. Использует блокировку строк БД (select_for_update), чтобы
       предотвратить состояние гонки (race condition) при конкурентных покупках.
    3. Списывает остатки и рассчитывает итоговую сумму.
    4. Создает все записи в БД в рамках одной атомарной транзакции (transaction.atomic)
       с использованием bulk_create для максимальной производительности.
    """

    items = OrderItemCreateSerializer(many=True)

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        with transaction.atomic():
            order = Order.objects.create(client=user, total_amount=0)
            total_amount = 0

            product_ids = [item["product_id"] for item in items_data]

            products = Product.objects.select_for_update().filter(id__in=product_ids)

            products_map = {p.id: p for p in products}

            order_items_to_create = []

            for item in items_data:
                product_id = item["product_id"]
                quantity = item["quantity"]

                if product_id not in products_map:
                    raise serializers.ValidationError(f"Товар с ID {product_id} не найден.")

                product = products_map[product_id]

                if product.stock < quantity:
                    raise serializers.ValidationError(
                        f"Недостаточно товара '{product.name}'. Доступно: {product.stock}"
                    )

                product.stock -= quantity
                product.save(update_fields=["stock"])

                item_total = product.price * quantity
                total_amount += item_total

                order_items_to_create.append(
                    OrderItem(order=order, product=product, quantity=quantity, price=product.price)
                )

            OrderItem.objects.bulk_create(order_items_to_create)

            order.total_amount = total_amount
            order.save(update_fields=["total_amount"])

        return order
