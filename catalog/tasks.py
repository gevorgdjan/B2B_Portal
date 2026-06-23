from typing import Any

import pandas as pd
from celery import shared_task
from django.core.files.storage import default_storage

from .models import Product
from .services import OneCSyncService


@shared_task(bind=True)
def process_price_list_task(self, file_path: str) -> dict[str, Any]:
    try:
        absolute_path = default_storage.path(file_path)

        df = pd.read_excel(absolute_path, engine='openpyxl')

        df = df.where(pd.notnull(df), None)

        created_count = 0
        updated_count = 0

        for index, row in df.iterrows():
            sku = str(row.get('sku', '')).strip()
            if not sku or sku == 'None':
                continue

            name = str(row.get('name', 'Без названия')).strip()
            price = pd.to_numeric(row.get('price'), errors='coerce')
            stock = pd.to_numeric(row.get('stock'), errors='coerce')

            product, created = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'price': price if pd.notna(price) else 0,
                    'stock': int(stock) if pd.notna(stock) else 0,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count
        }

    except Exception as e:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
        return {"status": "error", "message": str(e)}


@shared_task
def sync_1c_stocks_task():
    service = OneCSyncService()
    updated_count = service.sync_stocks()
    return f"Успешно обновлено {updated_count} позиций"