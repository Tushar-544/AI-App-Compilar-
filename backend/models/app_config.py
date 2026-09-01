from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

from .intent import IntentModel
from .architecture import ArchitectureModel
from .ui_schema import UISchemaModel
from .api_schema import APISchemaModel
from .db_schema import DBSchemaModel
from .auth_schema import AuthSchemaModel


class ValidationIssue(BaseModel):
    severity: str               # "error" | "warning"
    layer: str                  # "ui" | "api" | "db" | "auth" | "cross"
    issue: str
    field: Optional[str] = None
    auto_repaired: bool = False
    repair_action: Optional[str] = None


class PipelineStageResult(BaseModel):
    stage: int
    name: str
    success: bool
    latency_ms: int
    retries: int = 0
    error: Optional[str] = None


class PipelineMetadata(BaseModel):
    model_config = {"protected_namespaces": ()}
    original_prompt: str
    total_latency_ms: int
    stages: List[PipelineStageResult]
    total_retries: int
    validation_issues: List[ValidationIssue]
    repair_actions: List[str]
    assumptions: List[str]
    cost_estimate_usd: float
    model_used: str


class AppConfig(BaseModel):
    version: str = "1.0"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    intent: IntentModel
    architecture: ArchitectureModel
    ui_schema: UISchemaModel
    api_schema: APISchemaModel
    db_schema: DBSchemaModel
    auth_schema: AuthSchemaModel
    metadata: PipelineMetadata
    is_executable: bool = True
