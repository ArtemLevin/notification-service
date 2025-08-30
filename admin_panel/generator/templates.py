from sqlalchemy import select

from admin_panel.core.db import AsyncDBSession
from admin_panel.models import MessageTemplate


DEFAULT_TEMPLATES = [
    {
        "name": "welcome",
        "subject": "Добро пожаловать в наш сервис!",
        "body": """Здравствуйте, {{ user.name }}!

Спасибо, что присоединились к нашему сервису. Мы уверены, что впереди вас ждёт масса интересного: подборки фильмов, рекомендации и персональные скидки.

Сегодня {{ current_date|format_date("%d.%m.%Y") }} — отличный день, чтобы начать!"""
    },
    {
        "name": "recommendation",
        "subject": "Подборка фильмов специально для вас",
        "body": """Привет, {{ user.name }}!

Сегодня у нас для вас подборка фильмов:
{% for movie in extra.movies %}
- {{ movie.title }}
{% endfor %}

Желаем приятного просмотра!"""
    },
    {
        "name": "discount",
        "subject": "Ваш персональный подарок 🎁",
        "body": """Добрый день, {{ user.name }}!

У нас есть подарок специально для вас 🎁
Только сегодня {{ current_date|format_date("%d.%m.%Y") }} вы можете получить скидку {{ extra.discount }}% на подписку.

Активируйте предложение прямо сейчас и наслаждайтесь просмотром без ограничений!"""
    },
]


async def init_templates():
    async with AsyncDBSession() as session:
        for template in DEFAULT_TEMPLATES:
            result = await session.execute(select(MessageTemplate).where(MessageTemplate.name == template["name"]))
            exists = result.scalar_one_or_none()
            if not exists:
                session.add(MessageTemplate(**template))
        await session.commit()
