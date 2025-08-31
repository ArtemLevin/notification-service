from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from core.service import NotificationService, get_notification_service
from models.base import BaseResponse
from models.notification import (
    NotificationCreate,
    NotificationEvent,
    NotificationTemplateBase,
)

router = APIRouter(prefix="/api/v1", tags=["Notification API V1"])


@router.post("/notifications/send", status_code=201, response_model=BaseResponse,
             description="Отправка рассылок",
             responses={status.HTTP_201_CREATED: {"message": "Successfully sent", "model": BaseResponse}})
async def send_notification(
    notification: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    created = await service.send_notification(notification)
    return BaseResponse(success=True, message="Successfully sent", data=created)


@router.post("/notifications/events", status_code=201, response_model=BaseResponse,
             description="Прием событий",
             responses={status.HTTP_201_CREATED: {"message": "Successfully sent", "model": BaseResponse}})
async def send_event(
    event: NotificationEvent,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    result = await service.process_event(event)
    return BaseResponse(success=True, message="Successfully sent", data=result)


# --- выдача пользователю его уведомлений ---
@router.get("/users/{user_id}/notifications", response_model=BaseResponse,
            description="Получить уведомления пользователя")
async def user_notifications(
    user_id: str,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    items = await service.get_user_notifications(user_id)
    return BaseResponse(success=True, data=items)


# CRUD: Получить уведомление по id
@router.get(
    "/notifications/{notification_id}",
    response_model=BaseResponse,
    description="Получить уведомление по id",
)
async def get_notification(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    try:
        notification = await service.get_notification(notification_id)
        return BaseResponse(success=True, data=notification)
    except Exception as error:
        return BaseResponse(success=False, message=str(error))


# CRUD: Получить все уведомления
@router.get(
    "/notifications",
    response_model=BaseResponse,
    description="Получить все уведомления",
)
async def list_notifications(
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    notifications = await service.list_notifications()
    return BaseResponse(success=True, data=notifications)


# CRUD: Обновить уведомление
@router.patch(
    "/notifications/{notification_id}",
    response_model=BaseResponse,
    description="Обновить уведомление по id",
)
async def update_notification(
    notification_id: UUID,
    update_data: dict,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    try:
        notification = await service.update_notification(notification_id, update_data)
        return BaseResponse(success=True, data=notification)
    except Exception as error:
        return BaseResponse(success=False, message=str(error))


# CRUD: Удалить уведомление
@router.delete(
    "/notifications/{notification_id}",
    response_model=BaseResponse,
    description="Удалить уведомление по id",
)
async def delete_notification(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    try:
        await service.delete_notification(notification_id)
        return BaseResponse(success=True, message="Уведомление удалено")
    except Exception as error:
        return BaseResponse(success=False, message=str(error))


# CRUD: Получить шаблон по id
@router.get(
    "/templates/{template_id}",
    response_model=BaseResponse,
    description="Получить шаблон по id",
)
async def get_template(
    template_id: UUID,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    try:
        template = await service.get_template(template_id)
        return BaseResponse(success=True, data=template)
    except Exception as error:
        return BaseResponse(success=False, message=str(error))


# CRUD: Обновить шаблон
@router.patch(
    "/templates/{template_id}",
    response_model=BaseResponse,
    description="Обновить шаблон по id",
)
async def update_template(
    template_id: UUID,
    update_data: dict,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    try:
        template = await service.update_template(template_id, update_data)
        return BaseResponse(success=True, data=template)
    except Exception as error:
        return BaseResponse(success=False, message=str(error))


# CRUD: Удалить шаблон
@router.delete(
    "/templates/{template_id}",
    response_model=BaseResponse,
    description="Удалить шаблон по id",
)
async def delete_template(
    template_id: UUID,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    try:
        await service.delete_template(template_id)
        return BaseResponse(success=True, message="Шаблон удалён")
    except Exception as error:
        return BaseResponse(success=False, message=str(error))


@router.get(
    "/templates",
    response_model=List[NotificationTemplateBase],
    description="Получение списка шаблонов",
)
async def get_templates(
    service: NotificationService = Depends(get_notification_service),
) -> List[NotificationTemplateBase]:
    templates = await service.get_templates()
    return [NotificationTemplateBase.model_validate(template) for template in templates]


@router.post(
    "/templates",
    description="Создание шаблона",
    responses={
        status.HTTP_201_CREATED: {
            "message": "Successfully sent",
            "model": BaseResponse,
        },
    },
    status_code=201,
    response_model=BaseResponse,
)
async def create_template(
    template: NotificationTemplateBase,
    service: NotificationService = Depends(get_notification_service),
) -> BaseResponse:
    created = await service.create_template(template)
    return BaseResponse(success=True, message="Successfully sent", data=created)
