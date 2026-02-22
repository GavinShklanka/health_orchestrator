# app/graph/innovation_subgraph.py

def innovation_entry(state: dict) -> dict:
    state.setdefault("path_trace", [])
    state["path_trace"].append("innovation_entry")

    # Admin-only gate
    if state.get("role") != "admin":
        state["terminal_status"] = "ESCALATE"
        return state

    # Initialize sandbox only for admin
    state["innovation_mode"] = True
    state["sandbox"] = {
        "draft_policy_version": 1,
        "policy_notes": []
    }

    return state


def innovation_draft_node(state: dict) -> dict:
    state.setdefault("path_trace", [])
    state["path_trace"].append("innovation_draft_node")

    # Safety guard: sandbox must exist
    if "sandbox" not in state:
        state["terminal_status"] = "ESCALATE"
        return state

    draft = {
        "version": state["sandbox"]["draft_policy_version"],
        "proposal": "New scheduling workflow optimization",
        "impact_level": "moderate"
    }

    state["draft_summary"] = draft
    state["terminal_status"] = "WAITING_APPROVAL"

    return state