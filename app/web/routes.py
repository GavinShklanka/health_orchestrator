from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.db import get_connection

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT run_id, status, module, started_at
        FROM runs
        ORDER BY started_at DESC
        LIMIT 10
    """)

    runs = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "runs": runs
        }
    )