from langgraph.graph import StateGraph, END

# Core appointment nodes
from app.graph.nodes import (
    classify_intent,
    route_intent,
    schedule_node,
    reschedule_node,
    cancel_node,
    prep_node,
    unknown_node,
    execute_tool_node
)

# HITL nodes
from app.graph.hitl_nodes import draft_action, interrupt_for_approval

# Innovation nodes
from app.graph.innovation_subgraph import (
    innovation_entry,
    innovation_draft_node
)


def build_graph():

    workflow = StateGraph(dict)

    # -----------------------------
    # Core Classification
    # -----------------------------
    workflow.add_node("classify", classify_intent)

    # -----------------------------
    # Appointment Nodes
    # -----------------------------
    workflow.add_node("schedule_node", schedule_node)
    workflow.add_node("reschedule_node", reschedule_node)
    workflow.add_node("cancel_node", cancel_node)
    workflow.add_node("prep_node", prep_node)
    workflow.add_node("unknown_node", unknown_node)

    # -----------------------------
    # Innovation Nodes
    # -----------------------------
    workflow.add_node("innovation_entry", innovation_entry)
    workflow.add_node("innovation_draft_node", innovation_draft_node)

    # -----------------------------
    # HITL Nodes
    # -----------------------------
    workflow.add_node("draft_action", draft_action)
    workflow.add_node("interrupt_for_approval", interrupt_for_approval)
    workflow.add_node("execute_tool", execute_tool_node)

    workflow.set_entry_point("classify")

    # -----------------------------
    # Extended Intent Routing
    # -----------------------------
    def extended_route(state: dict) -> str:
        message = state.get("message", "").lower()

        if "innovate" in message or "policy" in message:
            return "innovation_entry"

        return route_intent(state)

    workflow.add_conditional_edges(
        "classify",
        extended_route,
        {
            "schedule_node": "schedule_node",
            "reschedule_node": "reschedule_node",
            "cancel_node": "cancel_node",
            "prep_node": "prep_node",
            "unknown_node": "unknown_node",
            "innovation_entry": "innovation_entry"
        }
    )

    # -----------------------------
    # Unknown Ends
    # -----------------------------
    workflow.add_edge("unknown_node", END)

    # -----------------------------
    # Appointment Flow
    # -----------------------------
    workflow.add_edge("schedule_node", "draft_action")
    workflow.add_edge("reschedule_node", "draft_action")
    workflow.add_edge("cancel_node", "draft_action")
    workflow.add_edge("prep_node", "draft_action")

    workflow.add_edge("draft_action", "interrupt_for_approval")

    workflow.add_conditional_edges(
        "interrupt_for_approval",
        lambda state: state.get("approved", False),
        {
            True: "execute_tool",
            False: END
        }
    )

    workflow.add_edge("execute_tool", END)

    # -----------------------------
    # Innovation Flow (FIXED)
    # -----------------------------
    workflow.add_conditional_edges(
        "innovation_entry",
        lambda state: state.get("terminal_status") == "ESCALATE",
        {
            True: END,
            False: "innovation_draft_node"
        }
    )

    workflow.add_edge("innovation_draft_node", END)

    return workflow.compile()