from uuid import UUID

from fastapi import APIRouter, status

from shared.models.base import BaseResponse
from shared.models.notification import NotificationCreate, NotificationEvent, \
    NotificationTemplate

router = APIRouter(prefix="/api/v1", tags=["Notification API V1"])


@router.post("/notifications/send", description="Отправка рассылок",
             responses={
                 status.HTTP_201_CREATED: {
                     "message": "Successfully sent",
                     "model": BaseResponse
                 }
             }, status_code=201)
async def send_notification(notification: NotificationCreate) -> BaseResponse:
    pass


@router.post("/notifications/events", description="Прием событий",
             responses={
                 status.HTTP_201_CREATED: {
                     "message": "Successfully sent",
                     "model": BaseResponse
                 }
             }, status_code=201)
async def send_event(event: NotificationEvent) -> BaseResponse:
    pass


@router.get("/notifications/user/{user_id}",
            description="Получение уведомлений пользователя")
async def send_notification_to_user(user_id: UUID) -> BaseResponse:
    pass


@router.get("/templates",
            response_model=list[NotificationTemplate],
            description="Получение списка шаблонов")
async def get_templates() -> list[NotificationTemplate]:
    pass


@router.post("/templates", description="Создание шаблона",
             responses={
                 status.HTTP_201_CREATED: {
                     "message": "Successfully sent",
                     "model": BaseResponse
                 }
             }, status_code=201)
async def create_template(template: NotificationTemplate) -> BaseResponse:
    pass


@router.get("/health", description="Health Check")
async def health_check() -> BaseResponse:
    return BaseResponse(success=True, message="Ok")
