import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "health_orchestrator.db")

MIDDLEWARE_VERSION = "1.0"
POLICY_PACK_VERSION = "1.0"
MODEL_NAME = "N/A"
TEMPERATURE = 0.0