Использование и ручные проверки

Ниже приведён пошаговый сценарий запуска и проверки всех компонентов системы рассылок.

---

## 1. Подготовка окружения
1. Скопируйте `.env.example` в `.env` и заполните значения:
   - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
   - `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`
   - `WEBSOCKET_SECRET`
   - при необходимости `LINK_SHORTENER_BASE_URL`

2. Соберите и запустите инфраструктуру:
   ```bash
   docker compose up --build
   ```
   Поднимутся сервисы:
   - `postgres` (БД)
   - `redis`
   - `rabbitmq` (с веб-интерфейсом на `http://localhost:15672`)
   - `notification_api` (REST API, порт `8002`)
   - `admin` (админ-панель, порт `8001`)
   - `link-shortener` (порт `8000`)
   - `worker` (фоновая обработка)
   - `websocket-server` (порт `8004`)

---

## 2. CRUD шаблонов сообщений
1. Создайте шаблон уведомления:
   ```bash
   curl -X POST http://localhost:8002/api/v1/templates      -H "Content-Type: application/json"      -d '{
       "name": "welcome_email",
       "subject": "Добро пожаловать, {{user.name}}!",
       "body": "Здравствуйте, {{user.name}}! Спасибо за регистрацию.",
       "notification_type": "email"
     }'
   ```

2. Получите список шаблонов:
   ```bash
   curl http://localhost:8002/api/v1/templates
   ```

---

## 3. Немедленная отправка уведомления
```bash
curl -X POST http://localhost:8002/api/v1/notifications/send   -H "Content-Type: application/json"   -d '{
    "template_id": "<UUID шаблона>",
    "recipients": ["ALL"],
    "notification_type": "email",
    "data": {"links": ["https://example.com"]}
  }'
```

- В `worker`-контейнере появится лог вида `EMAIL_SENT`.

---

## 4. Отложенные уведомления
Укажите поле `scheduled_time`:
```bash
curl -X POST http://localhost:8002/api/v1/notifications/send   -H "Content-Type: application/json"   -d '{
    "template_id": "<UUID шаблона>",
    "recipients": ["user-123"],
    "notification_type": "email",
    "scheduled_time": "2025-09-01T10:00:00Z"
  }'
```

- Уведомление попадёт в БД со статусом `pending`.
- Планировщик воркера отправит его в указанное время.

---

## 5. Повторяющиеся уведомления
```bash
curl -X POST http://localhost:8002/api/v1/notifications/send   -H "Content-Type: application/json"   -d '{
    "template_id": "<UUID шаблона>",
    "recipients": ["ALL"],
    "notification_type": "push",
    "is_recurring": true,
    "recurrence_pattern": "weekly:FRI"
  }'
```

- Каждую пятницу в 9:00 воркер будет перепланировать и публиковать сообщение.

---

## 6. События во внешнем формате
Пример регистрации пользователя:
```bash
curl -X POST http://localhost:8002/api/v1/notifications/events   -H "Content-Type: application/json"   -d '{
    "event_type": "user_registered",
    "user_id": "user-123",
    "data": {"template_id": "<UUID шаблона>"}
  }'
```

- API преобразует событие в создание уведомления.

---

## 7. Получение уведомлений пользователем
```bash
curl http://localhost:8002/api/v1/users/user-123/notifications
```

---

## 8. WebSocket-подключение
1. Получите токен:
   ```python
   import hmac, hashlib
   secret = b"dev-secret"
   user_id = "user-123"
   token = hmac.new(secret, user_id.encode(), hashlib.sha256).hexdigest()
   print(token)
   ```

2. Подключитесь:
   ```bash
   websocat "ws://localhost:8004/ws?user_id=user-123&token=<token>"
   ```

3. Отправьте `instant` уведомление:
   ```bash
   curl -X POST http://localhost:8002/api/v1/notifications/send      -H "Content-Type: application/json"      -d '{
       "template_id": "<UUID шаблона>",
       "recipients": ["user-123"],
       "notification_type": "instant"
     }'
   ```

4. Сообщение появится в WebSocket-подключении.

---

## 9. Проверка сокращения ссылок
```bash
curl -X POST http://localhost:8000/shorten   -H "Content-Type: application/json"   -d '{"original_url":"https://example.com/some/long/path"}'
```

- В ответ придёт объект с `short_url`, который будет использоваться в теле уведомления.

---
