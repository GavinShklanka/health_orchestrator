# app/api/session.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.db import get_connection

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_run(run_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
    run = cursor.fetchone()

    conn.close()
    return run


def get_events(run_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM events
        WHERE run_id = ?
        ORDER BY timestamp ASC
    """, (run_id,))

    events = cursor.fetchall()
    conn.close()
    return events


def resolve_final_message(events):
    """
    Safely determine final user-facing message.
    Uses last event summary.
    """
    if not events:
        return None

    return events[-1]["summary"]


@router.get("/session/{run_id}", response_class=HTMLResponse)
def session_view(request: Request, run_id: str):

    run = get_run(run_id)

    if not run:
        return HTMLResponse("Run not found", status_code=404)

    events = get_events(run_id)
    final_message = resolve_final_message(events)

    return templates.TemplateResponse(
        "session.html",
        {
            "request": request,
            "run": run,
            "events": events,
            "final_message": final_message,
            "auto_refresh": run["status"] == "RUNNING"
        }
    )