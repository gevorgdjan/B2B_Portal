from split_settings.tools import include, optional
import os

# По умолчанию запускаем локальные настройки
ENV = os.getenv('DJANGO_ENV', 'local')

base_settings = [
    'base.py', # Общие настройки
    f'{ENV}.py', # Специфичные для среды (local.py или production.py)
]

# Склеиваем настройки
include(*base_settings)