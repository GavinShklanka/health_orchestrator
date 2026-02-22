#hitl_nodes.py
from app.services.approvals import create_approval
from app.services.run_registry import update_status


# ---- Draft Node ----
def draft_action(state: dict) -> dict:
    """
    Prepare a draft action for approval.
    """
    state["draft_summary"] = {
        "intent": state.get("intent"),
        "proposed_tool": state.get("tool_name"),
        "proposed_input": state.get("tool_input")
    }

    state["terminal_status"] = "WAITING_APPROVAL"
    return state


# ---- Interrupt Node ----
def interrupt_for_approval(state: dict) -> dict:
    """
    Mark run as waiting approval and return control to CLI.
    """
    update_status(state["run_id"], "WAITING_APPROVAL")
    return state


# ---- Resume After Approval ----
def resume_after_approval(state: dict) -> dict:
    """
    Continue execution after approval.
    """
    update_status(state["run_id"], "RUNNING")
    return state