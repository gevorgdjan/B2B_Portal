# B2B ERP API (Django REST Framework + Celery)

Полноценный бэкенд для B2B-портала (Склад и Заказы). Проект спроектирован с упором на принципы **SOLID**, **ООП** и чистую архитектуру. Бизнес-логика вынесена в Service Layer, а тяжелые задачи обрабатываются асинхронно.

## 🛠 Технологический стек
*   **Язык и Фреймворк:** Python 3.12, Django 5.2, Django REST Framework 3.16
*   **База данных:** PostgreSQL (`psycopg 3`)
*   **Асинхронность и Очереди:** Celery, RabbitMQ (Broker), Redis (Result Backend)
*   **Интеграции и Данные:** `pandas`, `openpyxl` (импорт Excel), `PyOData1C` (синхронизация с 1С)
*   **Авторизация:** Кастомная реализация JWT (на базе `PyJWT`)
*   **Документация:** Swagger / OpenAPI 3.0 (`drf-spectacular`)
*   **Качество кода:** Ruff (линтер), Mypy (строгая типизация), django-split-settings

## 🚀 Ключевые архитектурные решения

1.  **Кастомная модель пользователя:** Отказ от стандартного `username` в пользу авторизации по `email`. Реализована ролевая модель (RBAC: Менеджер, Кладовщик, Клиент).
2.  **Service Layer (Слой сервисов):** Толстые модели и контроллеры (Fat Models/Views) избегаются. Вся бизнес-логика (генерация токенов, работа с 1С) инкапсулирована в сервисы (SRP принцип).
3.  **Фоновая обработка файлов:** Загрузка прайс-листов (Excel) реализована асинхронно. Контроллер лишь сохраняет файл и отдает задачу в **Celery**, где **Pandas** парсит десятки тысяч строк, не блокируя HTTP-запрос.
4.  **Периодические задачи (Cron):** Настроена интеграция с `django-celery-beat` для регулярной синхронизации остатков с 1С по протоколу OData.
5.  **Безопасность конфигураций:** Разделение настроек на Local/Production (`split-settings`), использование переменных окружения (`.env`) и ленивых импортов для избежания конфликтов библиотек Rust/C.

## 🛠 Установка и запуск (Docker)

Для запуска проекта потребуется [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/).

### Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/gevorgdjan/B2B_Portal.git
cd erp_portal
```

### Шаг 2: Настройка переменных окружения
Создайте файл `.env` в корне проекта на основе примера (если есть `.env.example`, либо используйте конфигурацию ниже):

```env
DJANGO_SECRET_KEY=your-super-secret-key-123
DJANGO_DEBUG=True
DJANGO_ENV=local

DB_NAME=erp_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Шаг 3: Сборка и запуск контейнеров
Выполните команду для поднятия всей инфраструктуры (БД, Брокер, Кэш, Веб-сервер, Celery Worker и Beat):

```bash
docker-compose up --build -d
```
*Примечание: Миграции базы данных применяются автоматически при старте веб-контейнера.*

### Шаг 4: Создание администратора
Чтобы зайти в панель управления, создайте суперпользователя:

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 📖 Документация API (Swagger)

После успешного запуска сервера интерактивная документация API будет доступна по адресам:
* **Swagger UI:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
* **OpenAPI Schema (JSON):** [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

Для тестирования защищенных эндпоинтов:
1. Выполните метод `POST /api/v1/users/login/`
2. Скопируйте полученный JWT-токен.
3. Нажмите кнопку **Authorize** в Swagger и вставьте токен.
4. После авторизации все эндпоинты станут доступны.

## 🗄 Структура проекта
```text
erp_portal/
├── config/             # Ядро Django, настройки (split-settings), роутинг, Celery-app
├── users/              # Кастомная модель пользователя, JWT-авторизация, RBAC
├── catalog/            # Товары, асинхронный импорт Excel (Pandas), синхронизация с 1С
├── orders/             # Управление заказами, сложные транзакции, связь с каталогом
├── docker-compose.yml  # Оркестрация контейнеров
├── Dockerfile          # Инструкции сборки веб-сервера и воркеров
└── requirements.txt    # Зависимости проекта
```
```
