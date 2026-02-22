# app/graph/nodes.py

# ==============================
# Intent Classification
# ==============================

def classify_intent(state: dict) -> dict:
    state.setdefault("path_trace", [])
    state["path_trace"].append("classify")

    message = state.get("message", "").lower()

    if "cancel" in message:
        state["intent"] = "cancel"
    elif "reschedule" in message:
        state["intent"] = "reschedule"
    elif "schedule" in message or "book" in message:
        state["intent"] = "schedule"
    elif "prepare" in message:
        state["intent"] = "prep"
    else:
        state["intent"] = "unknown"

    return state


# ==============================
# Intent Router
# ==============================

def route_intent(state: dict) -> str:
    if state["intent"] == "cancel":
        return "cancel_node"
    if state["intent"] == "reschedule":
        return "reschedule_node"
    if state["intent"] == "schedule":
        return "schedule_node"
    if state["intent"] == "prep":
        return "prep_node"
    return "unknown_node"


# ==============================
# Tool Preparation Nodes
# ==============================

def schedule_node(state: dict) -> dict:
    state["path_trace"].append("schedule_node")
    state["tool_name"] = "schedule_tool"
    state["tool_input"] = "appointment_data"
    return state


def reschedule_node(state: dict) -> dict:
    state["path_trace"].append("reschedule_node")
    state["tool_name"] = "reschedule_tool"
    state["tool_input"] = "appointment_id=123"
    return state


def cancel_node(state: dict) -> dict:
    state["path_trace"].append("cancel_node")
    state["tool_name"] = "cancel_tool"
    state["tool_input"] = "appointment_id=123"
    return state


def prep_node(state: dict) -> dict:
    state["path_trace"].append("prep_node")
    state["tool_name"] = "prep_instruction_tool"
    state["tool_input"] = "procedure_type"
    return state


def unknown_node(state: dict) -> dict:
    state["path_trace"].append("unknown_node")
    state["terminal_status"] = "NEED_INFO"
    return state


# ==============================
# Execution Node
# ==============================

from app.middleware.engine import MiddlewareEngine
from app.middleware.auth import AuthMiddleware
from app.middleware.validation import ValidationMiddleware
from app.middleware.redaction import RedactionMiddleware
from app.middleware.policy import PolicyMiddleware
from app.middleware.risk import RiskMiddleware
from app.middleware.tool_wrapper import ToolWrapperMiddleware


def middleware_stack():
    return MiddlewareEngine([
        AuthMiddleware(),
        ValidationMiddleware(),
        RedactionMiddleware(),
        PolicyMiddleware(),
        RiskMiddleware(),
        ToolWrapperMiddleware()
    ])


def execute_tool_node(state: dict) -> dict:
    # Remove approval marker if present
    state.pop("terminal_status", None)

    state.setdefault("path_trace", [])
    state["path_trace"].append("execute_tool")

    result = middleware_stack().run(state)

    return result