class BaseNotificationException(Exception):
    """Базовое исключение для системы уведомлений"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(BaseNotificationException):
    def __init__(self, message: str):
        super().__init__(message, 400)

class NotFoundException(BaseNotificationException):
    def __init__(self, message: str):
        super().__init__(message, 404)

class ServiceUnavailableException(BaseNotificationException):
    def __init__(self, message: str):
        super().__init__(message, 503)

class UnauthorizedException(BaseNotificationException):
    def __init__(self, message: str):
        super().__init__(message, 401)