import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Поиск по названию")
    sku = django_filters.CharFilter(lookup_expr="iexact", label="Точный артикул")

    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte", label="Цена от")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte", label="Цена до")

    in_stock = django_filters.BooleanFilter(method="filter_in_stock", label="Только в наличии")

    class Meta:
        model = Product
        fields = ["name", "sku"]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset
