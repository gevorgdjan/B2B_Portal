import logging
from typing import Any

# from pyodata1c import Client
from django.conf import settings

from .models import Product

logger = logging.getLogger(__name__)


class OneCSyncService:
    def __init__(self):
        self.odata_url = getattr(
            settings, "ONEC_ODATA_URL", "http://localhost/1c/odata/standard.odata/"
        )
        self.user = getattr(settings, "ONEC_USER", "Admin")
        self.password = getattr(settings, "ONEC_PASSWORD", "")
        # self.client = Client(self.odata_url, auth=(self.user, self.password))

    def fetch_stocks_from_1c(self) -> list[dict[str, Any]]:
        logger.info("Запрашиваем остатки из 1С...")

        mock_odata_response = [
            {"Article": "101", "Stock": 15},
            {"Article": "102", "Stock": 0},
            {"Article": "999", "Stock": 50},
        ]
        return mock_odata_response

    def sync_stocks(self):
        one_c_data = self.fetch_stocks_from_1c()

        updated_count = 0
        for item in one_c_data:
            sku = item.get("Article")
            stock = item.get("Stock", 0)
            updated = Product.objects.filter(sku=sku).update(stock=stock)
            if updated:
                updated_count += 1

        logger.info(f"Синхронизация с 1С завершена. Обновлено товаров: {updated_count}")
        return updated_count
