from datetime import datetime
from uuid import UUID as PyUUID

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import PlainTextResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin_panel.core.db import get_db_session
from admin_panel.models import MessageTemplate, Recipient
from admin_panel.admin.jinja_setup import jinja_env


router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/{template_id}/raw", response_class=PlainTextResponse)
async def get_raw_template(
    template_id: PyUUID,
    db: AsyncSession = Depends(get_db_session),
) -> PlainTextResponse:
    result = await db.execute(select(MessageTemplate).where(MessageTemplate.id == template_id))
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Шаблон не найден")

    return PlainTextResponse(template.body)


@router.get("/{template_id}/render", response_class=PlainTextResponse)
async def render_template(
    template_id: PyUUID,
    user_id: PyUUID,
    db: AsyncSession = Depends(get_db_session),
) -> PlainTextResponse:
    result = await db.execute(
        select(MessageTemplate).where(MessageTemplate.id == template_id)
    )
    template_obj = result.scalar_one_or_none()

    if not template_obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Шаблон не найден")
    
    result = await db.execute(
        select(Recipient).where(Recipient.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Получатель не найден")
    
    if template_obj.name == "recommendation":
        extra = {"movies": [{"title": "Матрица"}, {"title": "Интерстеллар"}, {"title": "Начало"}]} # get_movies_for_user(user)
    elif template_obj.name == "discount":
        extra = {"discount": "15"} # calculate_discount(user)
    else:
        extra = {}
    
    context = {
        "user": {"name": user.name, "email": user.email},
        "current_date": datetime.now(),
        "extra": extra,
    }

    try:
        j2_template = jinja_env.from_string(template_obj.body)
        rendered = j2_template.render(**context)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Ошибка рендера: {e}")

    return HTMLResponse(rendered)
