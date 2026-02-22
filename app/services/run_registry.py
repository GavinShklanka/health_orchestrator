import uuid
from datetime import datetime
from app.core.db import get_connection
from app.core.versioning import get_state_version
from app.core.config import MODEL_NAME, TEMPERATURE, MIDDLEWARE_VERSION, POLICY_PACK_VERSION

def create_run(user_id: str, tenant_id: str, module: str) -> str:
    run_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO runs (
            run_id, user_id, tenant_id, module, status,
            started_at, model_name, temperature,
            middleware_version, policy_pack_version, state_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id, user_id, tenant_id, module, "RUNNING",
        now, MODEL_NAME, TEMPERATURE,
        MIDDLEWARE_VERSION, POLICY_PACK_VERSION, get_state_version()
    ))

    conn.commit()
    conn.close()

    return run_id


def update_status(run_id: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE runs
        SET status = ?
        WHERE run_id = ?
    """, (status, run_id))

    conn.commit()
    conn.close()


def complete_run(run_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()

    cursor.execute("""
        UPDATE runs
        SET status = ?, ended_at = ?
        WHERE run_id = ?
    """, ("COMPLETED", now, run_id))

    conn.commit()
    conn.close()