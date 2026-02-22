from app.core.db import initialize_database

from app.core.config import DB_PATH
print("DB_PATH in CLI:", DB_PATH)
from app.services.run_registry import create_run, update_status, complete_run
from app.services.approvals import create_approval
from app.graph.orchestrator import build_graph


def format_output(state: dict) -> dict:
    display = state.copy()

    # Mask internal hashes
    if "tool_input_hash" in display:
        display["tool_input_hash"] = "[HASHED]"

    return display


def main():
    initialize_database()

    print("\n=== Agentic Appointment Engine (Governed Mode) ===\n")

    run_id = create_run(
        user_id="user_123",
        tenant_id="tenant_abc",
        module="HITL_TEST"
    )

    print(f"Run ID: {run_id}")

    user_role = input("Enter role (patient/admin): ").strip().lower()
    message_input = input("\nEnter your message: ").strip()

    state = {
    "run_id": run_id,
    "role": user_role,
    "message": message_input
    }

    graph = build_graph()
    result = graph.invoke(state)

    # ---------------------------------
    # HITL Handling (Appointment Flow)
    # ---------------------------------
    if result.get("terminal_status") == "WAITING_APPROVAL":

        update_status(run_id, "WAITING_APPROVAL")

        print("\n--- Draft Proposal ---")
        print(result.get("draft_summary"))

        decision = input("\nApprove action? (yes/no): ").strip().lower()

        if decision in ["yes", "y"]:

            print("\nApproval received. Executing...\n")

            create_approval(
                run_id=run_id,
                approved_by="admin_user",
                policy_level="standard",
                changes_summary="Approved via CLI"
            )

            update_status(run_id, "RUNNING")

            # Reset trace before resume
            result["approved"] = True
            result["path_trace"] = []

            result = graph.invoke(result)

        else:
            print("\nAction rejected.\n")
            update_status(run_id, "FAILED")
            complete_run(run_id)
            return

    # ---------------------------------
    # Terminal Status Determination
    # ---------------------------------
    terminal = "SUCCESS"

    if result.get("terminal_status") == "ESCALATE":
        terminal = "ESCALATED"
    elif result.get("risk_flag"):
        terminal = "ESCALATED"
    elif result.get("terminal_status") == "NEED_INFO":
        terminal = "NEED_INFO"
    elif result.get("terminal_status") == "FAILED":
        terminal = "FAILED"

    update_status(run_id, terminal)
    complete_run(run_id)

    # ---------------------------------
    # Output Formatting
    # ---------------------------------
    formatted = format_output(result)

    print("\n=== EXECUTION SUMMARY ===")
    print(f"Terminal Status : {terminal}")
    print(f"Intent          : {formatted.get('intent')}")
    print(f"Path Trace      : {formatted.get('path_trace')}")
    print(f"Tool Executed   : {formatted.get('tool_name')}")
    print(f"Tool Result     : {formatted.get('tool_result')}")
    print("\n==========================\n")


if __name__ == "__main__":
    main()