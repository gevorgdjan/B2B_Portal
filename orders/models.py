from django.db import models

from catalog.models import Product
from users.models import User


class Order(models.Model):
    """
    Модель заказа клиента (Заголовок документа).

    Связывает пользователя (клиента) с набором товаров.
    Хранит итоговую сумму (total_amount) для оптимизации запросов к БД,
    чтобы избежать агрегации SUM() при каждом чтении списка заказов.
    """

    class Status(models.TextChoices):
        NEW = "NEW", "Новый"
        PAID = "PAID", "Оплачен"
        CANCELLED = "CANCELLED", "Отменен"

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Заказ #{self.id} от {self.client.email}"


class OrderItem(models.Model):
    """
    Модель строки заказа (Табличная часть).

    Связывает конкретный заказ с товаром.
    Цена (price) фиксируется на момент создания записи, чтобы
    изменение цен в каталоге в будущем не влияло на историю заказов.
    """
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")

    quantity = models.PositiveIntegerField("Количество")
    price = models.DecimalField("Цена за единицу", max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
