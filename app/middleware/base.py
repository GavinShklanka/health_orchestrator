# app/middleware/base.py

class MiddlewareException(Exception):
    pass


class Middleware:
    def __init__(self, name: str):
        self.name = name

    def process(self, context: dict) -> dict:
        raise NotImplementedError("Middleware must implement process()")