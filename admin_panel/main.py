from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqladmin import Admin

from admin_panel.admin.views import MessageTemplateAdmin, CampaignAdmin, RecipientAdmin, DeliveryHistoryAdmin
from admin_panel.core.config import settings
from admin_panel.core.db import engine
from admin_panel.admin.auth import AdminAuth
from admin_panel.api.v1.routers import templates
from admin_panel.generator import init_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup actions")
    await init_all()
    yield
    print("Shutdown actions")


app = FastAPI(title=settings.common.name, description=settings.common.description, lifespan=lifespan)
app.include_router(templates.router)

# Admin
authentication_backend = AdminAuth(secret_key="your-secret-key")
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(MessageTemplateAdmin)
admin.add_view(CampaignAdmin)
admin.add_view(RecipientAdmin)
admin.add_view(DeliveryHistoryAdmin)