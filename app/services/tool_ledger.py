import hashlib
from datetime import datetime
from app.core.db import get_connection

def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def record_tool_call(run_id: str, tool_name: str, tool_input: str, result: str):
    input_hash = _hash_content(tool_input)
    result_hash = _hash_content(result)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tool_ledger (
            run_id, tool_name, input_hash,
            result_hash, executed_at, idempotency_key
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        tool_name,
        input_hash,
        result_hash,
        datetime.utcnow().isoformat(),
        f"{run_id}:{tool_name}:{input_hash}"
    ))

    conn.commit()
    conn.close()