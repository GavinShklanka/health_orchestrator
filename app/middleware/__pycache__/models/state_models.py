from pydantic import BaseModel
from typing import Optional, List

class OrchestratorState(BaseModel):
    run_id: str
    user_id: str
    tenant_id: str
    module: str
    terminal_status: Optional[str] = None
    state_version: int


class ExecutionState(BaseModel):
    path_trace: List[str] = []
    model_name: str
    temperature: float
    middleware_version: str
    prompt_version: str