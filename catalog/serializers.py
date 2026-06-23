from rest_framework import serializers

from .models import Product


class PriceListUploadSerializer(serializers.Serializer):
    """
    Сериализатор (DTO) для валидации входящего файла прайс-листа.

    Обеспечивает первичную безопасность, отсекая файлы с неверным расширением
    до того, как они попадут в файловую систему и будут переданы в очередь Celery.
    """

    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith(('.xls', '.xlsx')):
            raise serializers.ValidationError("Допускаются только файлы Excel (.xls, .xlsx)")
        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'sku', 'slug', 'price', 'stock')