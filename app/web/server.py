# app/web/server.py
from app.web.app import app  # re-export the real app
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def get_db():
    return sqlite3.connect("health_orchestrator.db")


# ======================================================
# DASHBOARD (Split Pane + Filtering)
# ======================================================

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, status: str = None, selected: str = None):

    conn = get_db()
    cursor = conn.cursor()

    # Filter runs
    if status:
        cursor.execute(
            "SELECT run_id, status, module, started_at FROM runs WHERE status=? ORDER BY started_at DESC",
            (status,)
        )
    else:
        cursor.execute(
            "SELECT run_id, status, module, started_at FROM runs ORDER BY started_at DESC"
        )

    runs = cursor.fetchall()

    # Aggregation counts
    cursor.execute("SELECT status, COUNT(*) FROM runs GROUP BY status")
    counts_raw = cursor.fetchall()
    counts = {row[0]: row[1] for row in counts_raw}

    # Selected run detail
    selected_run = None
    if selected:
        cursor.execute("SELECT * FROM runs WHERE run_id=?", (selected,))
        selected_run = cursor.fetchone()

    conn.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "runs": runs,
            "counts": counts,
            "active_filter": status,
            "selected_run": selected_run
        }
    )


# ======================================================
# RUN DETAIL (Standalone Page)
# ======================================================

@app.get("/run/{run_id}", response_class=HTMLResponse)
def run_detail(request: Request, run_id: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM runs WHERE run_id=?", (run_id,))
    run = cursor.fetchone()

    conn.close()

    return templates.TemplateResponse(
        "run_detail.html",
        {
            "request": request,
            "run": run
        }
    )


# ======================================================
# INNOVATION (Admin Sandbox Page)
# ======================================================

@app.get("/innovation", response_class=HTMLResponse)
def innovation(request: Request):
    return templates.TemplateResponse(
        "innovation.html",
        {"request": request}
    )


# ======================================================
# APPOINTMENT ENGINE PAGE (Web CLI Surface)
# ======================================================

@app.get("/appointment", response_class=HTMLResponse)
def appointment(request: Request):
    return templates.TemplateResponse(
        "appointment.html",
        {"request": request}
    )


# ======================================================
# APPROVALS PAGE (Live Governance Queue)
# ======================================================

@app.get("/approvals", response_class=HTMLResponse)
def approvals(request: Request):

    conn = get_db()
    cursor = conn.cursor()

    # Runs waiting for approval
    cursor.execute(
        "SELECT run_id, status, module, started_at FROM runs WHERE status='WAITING_APPROVAL' ORDER BY started_at DESC"
    )
    pending_runs = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        "approvals.html",
        {
            "request": request,
            "pending_runs": pending_runs
        }
    )


# ======================================================
# APPROVAL ACTION HANDLER (Approve / Reject)
# ======================================================

@app.post("/approvals/action")
def approval_action(
    run_id: str = Form(...),
    decision: str = Form(...)
):

    conn = get_db()
    cursor = conn.cursor()

    if decision == "approve":
        cursor.execute(
            "UPDATE runs SET status='RUNNING' WHERE run_id=?",
            (run_id,)
        )
    else:
        cursor.execute(
            "UPDATE runs SET status='FAILED' WHERE run_id=?",
            (run_id,)
        )

    conn.commit()
    conn.close()

    return RedirectResponse(url="/approvals", status_code=303)


# ======================================================
# AUDIT PAGE (Compliance View Placeholder)
# ======================================================

@app.get("/audit", response_class=HTMLResponse)
def audit(request: Request):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT run_id, tool_name, executed_at FROM tool_ledger ORDER BY executed_at DESC"
    )
    ledger = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        "audit.html",
        {
            "request": request,
            "ledger": ledger
        }
    )