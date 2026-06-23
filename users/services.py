from datetime import datetime, timedelta, timezone

from django.conf import settings

from .models import User


def generate_jwt_token(user: User) -> str:
    """
    Генерирует JWT токен для пользователя (Service Layer).

    Вынесение этой логики в отдельный слой позволяет отвязать криптографию
    и работу с токенами от контроллеров (Views), делая код тестируемым
    и переиспользуемым в разных частях приложения. Токен содержит `user_id`
    и срок действия (exp) в формате UTC.
    """

    import jwt

    payload = {
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),
        'iat': datetime.now(timezone.utc),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token