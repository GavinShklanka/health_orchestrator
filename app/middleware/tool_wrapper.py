# app/middleware/tool_wrapper.py

import hashlib
from app.middleware.base import Middleware
from app.services.tool_ledger import record_tool_call


class ToolWrapperMiddleware(Middleware):
    def __init__(self):
        super().__init__("ToolWrapperMiddleware")

    def process(self, context: dict) -> dict:
        tool = context.get("tool_name")
        tool_input = context.get("tool_input")

        if not tool or not tool_input:
            return context

        input_hash = hashlib.sha256(tool_input.encode()).hexdigest()
        context["tool_input_hash"] = input_hash

        # Simulated tool result (Phase 2 only)
        result = f"Executed {tool}"

        record_tool_call(
            run_id=context["run_id"],
            tool_name=tool,
            tool_input=tool_input,
            result=result
        )

        context["tool_result"] = result

        return context