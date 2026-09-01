from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal

VALID_LAYOUTS = {"full", "sidebar", "split", "centered", "dashboard"}
# Map common LLM-generated layout names to valid ones
LAYOUT_MAP = {
    "simple": "full",
    "list": "full",
    "form": "centered",
    "details": "sidebar",
    "grid": "dashboard",
    "table": "full",
    "main": "full",
    "default": "full",
}


class UIComponent(BaseModel):
    id: str
    type: str  # DataTable, Form, Card, Button, Chart, Stat, etc.
    label: Optional[str] = None
    entity: Optional[str] = None       # maps to DB table entity
    api_endpoint: Optional[str] = None # maps to API endpoint id
    props: Dict[str, Any] = Field(default_factory=dict)


class UIPage(BaseModel):
    id: str
    title: str
    route: str
    layout: str = "full"
    access: List[str]  # role names
    is_premium: bool = False
    components: List[UIComponent]
    meta_description: str = ""

    @field_validator("layout", mode="before")
    @classmethod
    def normalize_layout(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.lower().strip()
        if v in VALID_LAYOUTS:
            return v
        return LAYOUT_MAP.get(v, "full")


class UISchemaModel(BaseModel):
    pages: List[UIPage]
    theme: Literal["light", "dark", "auto"] = "dark"
    navigation_type: Literal["sidebar", "topbar", "both"] = "sidebar"
    primary_color: str = "#6366f1"
    brand_name: str

