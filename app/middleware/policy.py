# app/middleware/policy.py

from app.middleware.base import Middleware, MiddlewareException


class PolicyMiddleware(Middleware):
    def __init__(self):
        super().__init__("PolicyMiddleware")

    def process(self, context: dict) -> dict:
        if context.get("intent") == "clinical_advice":
            raise MiddlewareException("Clinical advice not allowed.")
        return context