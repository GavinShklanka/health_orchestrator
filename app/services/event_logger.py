from datetime import datetime
from app.core.db import get_connection

def log_event(run_id: str, node_name: str, event_type: str, summary: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (
            run_id, node_name, event_type, timestamp, summary
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        run_id,
        node_name,
        event_type,
        datetime.utcnow().isoformat(),
        summary
    ))

    conn.commit()
    conn.close()