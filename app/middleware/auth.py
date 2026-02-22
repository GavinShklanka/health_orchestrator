# app/middleware/auth.py

from app.middleware.base import Middleware, MiddlewareException


class AuthMiddleware(Middleware):
    def __init__(self):
        super().__init__("AuthMiddleware")

    def process(self, context: dict) -> dict:
        role = context.get("role")

        if role not in ["patient", "admin"]:
            raise MiddlewareException("Unauthorized role.")

        return context