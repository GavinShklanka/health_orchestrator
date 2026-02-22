# app/middleware/redaction.py

from app.middleware.base import Middleware


class RedactionMiddleware(Middleware):
    def __init__(self):
        super().__init__("RedactionMiddleware")

    def process(self, context: dict) -> dict:
        # simple mock redaction
        if "ssn" in context:
            context["ssn"] = "***REDACTED***"
        return context