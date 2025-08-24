from uuid import UUID

from fastapi import APIRouter

from shared.models.notification import NotificationCreate, NotificationEvent, \
    NotificationTemplate

router = APIRouter(prefix="/api/v1", tags=["Notification API V1"])


@router.get("/")
async def root():
    return {"message": "Notification API"}


@router.post("/notifications/send", description="Отправка рассылок")
async def send_notification(notification: NotificationCreate):
    pass


@router.post("/notifications/events", description="Прием событий")
async def send_event(event: NotificationEvent):
    pass


@router.get("/notifications/user/{user_id}",
            description="Получение уведомлений пользователя")
async def send_notification_to_user(user_id: UUID):
    pass


@router.get("/templates", description="Получение списка шаблонов")
async def get_templates() -> list[NotificationTemplate]:
    pass


@router.post("/templates", description="Создание шаблона")
async def create_template(template: NotificationTemplate):
    pass


@router.get("/health", description="Health Check")
async def health_check():
    return {"status": "ok"}
