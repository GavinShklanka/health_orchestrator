from datetime import datetime
from app.core.db import get_connection

def create_approval(run_id: str, approved_by: str, policy_level: str, changes_summary: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO approvals (
            run_id, approved_by, policy_level,
            approved_at, expiry, changes_summary
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        approved_by,
        policy_level,
        datetime.utcnow().isoformat(),
        None,
        changes_summary
    ))

    conn.commit()
    conn.close()