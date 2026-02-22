# app/middleware/validation.py

from app.middleware.base import Middleware, MiddlewareException


class ValidationMiddleware(Middleware):
    def __init__(self):
        super().__init__("ValidationMiddleware")

    def process(self, context: dict) -> dict:
        if not context.get("intent"):
            raise MiddlewareException("Missing required intent.")

        return context