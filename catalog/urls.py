from django.urls import path

from .views import ImportPriceListAPIView, ProductListAPIView

app_name = 'catalog'

urlpatterns = [
    path('import/', ImportPriceListAPIView.as_view(), name='import_price_list'),
    path('products/', ProductListAPIView.as_view(), name='product_list'),
]