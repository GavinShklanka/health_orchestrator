from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from app.core.db import get_connection, initialize_database

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup():
    initialize_database()


# ==========================================
# DASHBOARD
# ==========================================

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, status: str = "", selected: str = ""):
    conn = get_connection()

    # ==========================================
    # EXECUTIVE METRICS
    # ==========================================

    total_runs_row = conn.execute("SELECT COUNT(*) as n FROM runs").fetchone()
    total_runs = total_runs_row["n"] if total_runs_row else 0

    escalated_row = conn.execute(
        "SELECT COUNT(*) as n FROM runs WHERE status = 'ESCALATED'"
    ).fetchone()
    escalated_count = escalated_row["n"] if escalated_row else 0

    escalation_rate = (
        round((escalated_count / total_runs) * 100, 2)
        if total_runs > 0 else 0
    )

    completed_runs = conn.execute("""
        SELECT started_at, ended_at
        FROM runs
        WHERE ended_at IS NOT NULL
    """).fetchall()

    total_duration = 0
    duration_count = 0

    for r in completed_runs:
        try:
            start = datetime.fromisoformat(r["started_at"])
            end = datetime.fromisoformat(r["ended_at"])
            total_duration += (end - start).total_seconds()
            duration_count += 1
        except:
            pass

    avg_completion_time = (
        round(total_duration / duration_count, 2)
        if duration_count > 0 else 0
    )

    approval_rows = conn.execute("""
        SELECT r.started_at, a.approved_at
        FROM approvals a
        JOIN runs r ON r.run_id = a.run_id
    """).fetchall()

    total_latency = 0
    latency_count = 0

    for row in approval_rows:
        try:
            start = datetime.fromisoformat(row["started_at"])
            approved = datetime.fromisoformat(row["approved_at"])
            total_latency += (approved - start).total_seconds()
            latency_count += 1
        except:
            pass

    avg_approval_latency = (
        round(total_latency / latency_count, 2)
        if latency_count > 0 else 0
    )

    # ==========================================
    # GOVERNANCE OVERVIEW METRICS
    # ==========================================

    human_intervention_row = conn.execute("""
        SELECT COUNT(*) as n
        FROM runs
        WHERE status IN ('WAITING_APPROVAL','ESCALATED')
    """).fetchone()
    human_intervention = human_intervention_row["n"] if human_intervention_row else 0

    completed_runs_row = conn.execute("""
        SELECT COUNT(*) as n
        FROM runs
        WHERE status = 'COMPLETED'
    """).fetchone()
    completed_runs_count = completed_runs_row["n"] if completed_runs_row else 0

    automation_rate = round(
        ((total_runs - human_intervention) / total_runs) * 100, 2
    ) if total_runs > 0 else 0

    human_intervention_rate = round(
        (human_intervention / total_runs) * 100, 2
    ) if total_runs > 0 else 0

    escalation_frequency = round(
        (escalated_count / total_runs) * 100, 2
    ) if total_runs > 0 else 0

    control_completion_ratio = round(
        (completed_runs_count / total_runs) * 100, 2
    ) if total_runs > 0 else 0

    risk_exposure = escalation_frequency + human_intervention_rate

    # ==========================================
    # STATUS COUNTS
    # ==========================================

    counts = {
        "SUCCESS": 0,
        "ESCALATED": 0,
        "NEED_INFO": 0,
        "FAILED": 0,
        "RUNNING": 0,
        "WAITING_APPROVAL": 0,
        "COMPLETED": 0
    }

    rows = conn.execute("""
        SELECT status, COUNT(*) AS n
        FROM runs
        GROUP BY status
    """).fetchall()

    for row in rows:
        s = row["status"]
        if s in counts:
            counts[s] = row["n"]

    # ==========================================
    # RUN LIST (ESCALATION PRIORITIZED)
    # ==========================================

    if status:
        runs = conn.execute("""
            SELECT * FROM runs
            WHERE status = ?
            ORDER BY started_at DESC
        """, (status,)).fetchall()
    else:
        runs = conn.execute("""
            SELECT * FROM runs
            ORDER BY 
                CASE 
                    WHEN status = 'ESCALATED' THEN 1
                    WHEN status = 'WAITING_APPROVAL' THEN 2
                    WHEN status = 'NEED_INFO' THEN 3
                    WHEN status = 'RUNNING' THEN 4
                    ELSE 5
                END,
                started_at DESC
        """).fetchall()

    # ==========================================
    # PIPELINE GROUPING (CORRECT LOCATION)
    # ==========================================

    active_runs = [r for r in runs if r["status"] == "RUNNING"][:5]
    pending_runs = [r for r in runs if r["status"] == "WAITING_APPROVAL"][:5]
    escalated_runs = [r for r in runs if r["status"] == "ESCALATED"][:5]
    closed_runs = [r for r in runs if r["status"] == "COMPLETED"][:5]

    # ==========================================
    # SELECTED RUN DETAIL
    # ==========================================

    run = None
    approvals = []
    tools = []
    events = []
    risk_posture = None

    if selected:
        run = conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", (selected,)
        ).fetchone()

        approvals = conn.execute("""
            SELECT * FROM approvals
            WHERE run_id = ?
            ORDER BY approved_at ASC
        """, (selected,)).fetchall()

        tools = conn.execute("""
            SELECT * FROM tool_ledger
            WHERE run_id = ?
            ORDER BY executed_at ASC
        """, (selected,)).fetchall()

        events = conn.execute("""
            SELECT * FROM events
            WHERE run_id = ?
            ORDER BY timestamp ASC
        """, (selected,)).fetchall()

        if run:
            if run["status"] == "ESCALATED":
                risk_posture = "CRITICAL"
            elif run["status"] == "WAITING_APPROVAL":
                risk_posture = "ELEVATED"
            elif run["status"] == "RUNNING":
                risk_posture = "MONITORING"
            else:
                risk_posture = "STABLE"

    # ==========================================
    # MIDDLEWARE HEATMAP
    # ==========================================

    middleware_counts = conn.execute("""
        SELECT node_name, COUNT(*) as n
        FROM events
        WHERE event_type = 'MIDDLEWARE'
        GROUP BY node_name
        ORDER BY n DESC
    """).fetchall() 
    
    max_middleware = 0
    if middleware_counts:
        max_middleware = max([row["n"] for row in middleware_counts])

        normalized_middleware = []
        for row in middleware_counts:
            intensity = 0
        if max_middleware > 0:
            intensity = round((row["n"] / max_middleware) * 100, 2)

    normalized_middleware.append({
        "node_name": row["node_name"],
        "count": row["n"],
        "intensity": intensity
    })
    

    conn.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "runs": runs,
        "counts": counts,
        "active_filter": status,
        "selected_run": run,
        "approvals": approvals,
        "tools": tools,
        "events": events,
        "total_runs": total_runs,
        "escalation_rate": escalation_rate,
        "avg_completion_time": avg_completion_time,
        "avg_approval_latency": avg_approval_latency,
        "middleware_counts": normalized_middleware,
        "risk_posture": risk_posture,
        "automation_rate": automation_rate,
        "human_intervention_rate": human_intervention_rate,
        "escalation_frequency": escalation_frequency,
        "control_completion_ratio": control_completion_ratio,
        "risk_exposure": risk_exposure,
        "active_runs": active_runs,
        "pending_runs": pending_runs,
        "escalated_runs": escalated_runs,
        "closed_runs": closed_runs,
    })

# ==========================================
# APPROVALS PAGE
# ==========================================

@app.get("/approvals", response_class=HTMLResponse)
def approvals_page(request: Request):
    conn = get_connection()

    pending_runs = conn.execute("""
        SELECT run_id, status, module, started_at
        FROM runs
        WHERE status = 'WAITING_APPROVAL'
        ORDER BY started_at DESC
    """).fetchall()

    conn.close()

    return templates.TemplateResponse("approvals.html", {
        "request": request,
        "pending_runs": pending_runs
    })
    approvals = conn.execute("""
        SELECT
            a.id,
            a.run_id,
            r.module,
            r.status AS run_status,
            a.approved_by,
            a.policy_level,
            a.approved_at,
            a.expiry,
            a.changes_summary
        FROM approvals a
        LEFT JOIN runs r ON r.run_id = a.run_id
        ORDER BY a.approved_at DESC
    """).fetchall()

    conn.close()

    return templates.TemplateResponse("approvals.html", {
        "request": request,
        "pending_runs": pending_runs,
        "approvals": approvals
    })


# ==========================================
# AUDIT PAGE
# ==========================================

@app.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, run_id: str = ""):
    conn = get_connection()

    if run_id:
        events = conn.execute("""
            SELECT *
            FROM events
            WHERE run_id = ?
            ORDER BY timestamp DESC
        """, (run_id,)).fetchall()
    else:
        events = conn.execute("""
            SELECT *
            FROM events
            ORDER BY timestamp DESC
        """).fetchall()

    recent_runs = conn.execute("""
        SELECT run_id, status, module, started_at
        FROM runs
        ORDER BY started_at DESC
        LIMIT 50
    """).fetchall()

    conn.close()

    return templates.TemplateResponse("audit.html", {
        "request": request,
        "events": events,
        "run_id": run_id,
        "recent_runs": recent_runs
    })


# ==========================================
# INNOVATION PAGE
# ==========================================

@app.get("/innovation", response_class=HTMLResponse)
def innovation_page(request: Request):
    conn = get_connection()

    drafts = conn.execute("""
        SELECT
            run_id, status, module, started_at, ended_at,
            middleware_version, policy_pack_version, state_version,
            model_name, temperature
        FROM runs
        WHERE UPPER(module) LIKE '%INNOV%' OR UPPER(module) LIKE '%DRAFT%'
        ORDER BY started_at DESC
        LIMIT 100
    """).fetchall()

    recent = conn.execute("""
        SELECT run_id, status, module, started_at
        FROM runs
        ORDER BY started_at DESC
        LIMIT 25
    """).fetchall()

    conn.close()

    return templates.TemplateResponse("innovation.html", {
        "request": request,
        "drafts": drafts,
        "recent": recent
    })


# ==========================================
# SESSION VIEW (NEW ADDITION ONLY)
# ==========================================

@app.get("/session/{run_id}", response_class=HTMLResponse)
def session_view(request: Request, run_id: str):
    conn = get_connection()

    run = conn.execute(
        "SELECT * FROM runs WHERE run_id = ?",
        (run_id,)
    ).fetchone()

    if not run:
        conn.close()
        return HTMLResponse("Run not found", status_code=404)

    events = conn.execute("""
        SELECT *
        FROM events
        WHERE run_id = ?
        ORDER BY timestamp ASC
    """, (run_id,)).fetchall()

    conn.close()

    final_message = events[-1]["summary"] if events else None

    return templates.TemplateResponse("session.html", {
        "request": request,
        "run": run,
        "events": events,
        "final_message": final_message,
        "auto_refresh": run["status"] == "RUNNING"
    })


# ==========================================
# APPOINTMENT ROUTES
# ==========================================

@app.get("/appointment", response_class=HTMLResponse)
def appointment_form(request: Request):
    return templates.TemplateResponse("appointment.html", {
        "request": request
    })
@app.post("/appointment")
def submit_appointment(
    module: str = Form(...),
    user_id: str = Form(...),
    tenant_id: str = Form(...),
    message: str = Form(...)
):
    conn = get_connection()

    run_id = f"run_{datetime.utcnow().timestamp()}"

    conn.execute("""
        INSERT INTO runs (
            run_id,
            user_id,
            tenant_id,
            module,
            status,
            started_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        user_id,
        tenant_id,
        module,
        "RUNNING",
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    # ==============================
    # Inject state into orchestration
    # ==============================

    from app.graph.orchestrator import build_graph

    state = {
        "run_id": run_id,
        "module": module,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "message": message,
        "approved": False
    }

    graph = build_graph()
    graph.invoke(state)

    return RedirectResponse(
        url=f"/session/{run_id}",
        status_code=303
    )

@app.post("/approve/{run_id}")
@app.post("/approve/{run_id}")
def approve_run(run_id: str):

    from app.graph.orchestrator import build_graph
    from app.services.run_registry import update_status
    from app.services.event_logger import log_event

    # Mark run as RUNNING
    update_status(run_id, "RUNNING")

    # Reconstruct minimal state for continuation
    state = {
        "run_id": run_id,
        "approved": True
    }

    from app.services.approvals import create_approval

    create_approval(
    run_id=run_id,
    approved_by="Admin",
    policy_level="STANDARD",
    changes_summary="Approved via UI"
)

    graph = build_graph()
    graph.invoke(state)

    log_event(
        run_id=run_id,
        node_name="HITL_APPROVAL",
        event_type="APPROVED",
        summary="Human approved execution"
    )

    return RedirectResponse(
        url=f"/session/{run_id}",
        status_code=303
    )

@app.post("/reject/{run_id}")
def reject_run(run_id: str):
    from app.services.run_registry import update_status

    update_status(run_id, "ESCALATED")

    return RedirectResponse(
        url=f"/session/{run_id}",
        status_code=303
    )