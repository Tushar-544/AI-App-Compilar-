from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Literal, Optional

# Map common LLM-generated strategy names to valid ones
STRATEGY_MAP = {
    "jwt": "JWT",
    "session": "Session",
    "session-based": "Session",
    "sessions": "Session",
    "cookie": "Session",
    "cookie-based": "Session",
    "oauth": "OAuth",
    "oauth2": "OAuth",
    "oauth2.0": "OAuth",
    "jwt+oauth": "JWT+OAuth",
    "jwt_oauth": "JWT+OAuth",
    "token": "JWT",
    "token-based": "JWT",
    "bearer": "JWT",
}


class PermissionEntry(BaseModel):
    resource: str                     # e.g. "contacts"
    permissions: Dict[str, str]       # role -> "CRUD" string
    # C=Create R=Read U=Update D=Delete


class PremiumGate(BaseModel):
    feature: str
    description: str = ""
    required_plan: str = "free"
    fallback_behavior: str = "deny"


class AuthSchemaModel(BaseModel):
    strategy: str = "JWT"
    access_token_expiry_minutes: int = 60
    refresh_token_expiry_days: int = 30
    roles: List[str]
    default_role: str
    permission_matrix: List[PermissionEntry]
    premium_gates: List[PremiumGate] = Field(default_factory=list)
    protected_routes: List[str] = Field(default_factory=list)
    public_routes: List[str] = Field(default_factory=list)
    mfa_required_roles: List[str] = Field(default_factory=list)

    @field_validator("strategy", mode="before")
    @classmethod
    def normalize_strategy(cls, v: str) -> str:
        if isinstance(v, str):
            normalized = v.lower().strip()
            if normalized in STRATEGY_MAP:
                return STRATEGY_MAP[normalized]
            # Check if it's already a valid value (case-insensitive)
            for valid in ["JWT", "Session", "OAuth", "JWT+OAuth"]:
                if normalized == valid.lower():
                    return valid
        return "JWT"  # safe default

