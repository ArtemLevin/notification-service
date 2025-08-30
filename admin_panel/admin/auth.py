from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from admin_panel.core.config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        login, password = form["username"], form["password"]
        
        if login == settings.admin.login.get_secret_value() and password == settings.admin.password.get_secret_value():
            request.session["user"] = login
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "user" in request.session

 