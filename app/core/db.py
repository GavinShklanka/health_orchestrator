from app.core.config import DB_PATH
print("DB_PATH in get_connection():", DB_PATH)

import sqlite3
import os
from app.core.config import DB_PATH


# =====================================================
# CONNECTION HELPER (Upgraded)
# =====================================================

#def get_connection():
"""
    Centralized DB connection.
    Adds row_factory so templates can use dict-style access.
    """
   # conn = sqlite3.connect(DB_PATH)
    #conn.row_factory = sqlite3.Row
   # return conn
def get_connection():
    print("DB_PATH in get_connection():", DB_PATH)  # TEMP DEBUG
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =====================================================
# DATABASE INITIALIZATION
# =====================================================

def initialize_database():
    """
    Initializes database using schema.sql.
    Preserves existing schema-driven approach.
    """

    if not os.path.exists(DB_PATH):
        print("Creating database...")

    conn = get_connection()
    cursor = conn.cursor()

    if not os.path.exists("schema.sql"):
        raise FileNotFoundError(
            "schema.sql not found. Database cannot be initialized."
        )

    with open("schema.sql", "r", encoding="utf-8") as f:
        schema_script = f.read()

    cursor.executescript(schema_script)
    conn.commit()
    conn.close()

    print("Database initialized successfully.")