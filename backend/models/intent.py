from pydantic import BaseModel, Field
from typing import List, Literal


class IntentModel(BaseModel):
    app_type: str = Field(..., description="Type of application e.g. CRM, LMS, E-commerce")
    app_name: str = Field(..., description="Suggested name for the application")
    primary_entities: List[str] = Field(..., description="Core data entities e.g. User, Product, Order")
    features: List[str] = Field(..., description="Features to be implemented")
    user_roles: List[str] = Field(..., description="User roles in the system")
    constraints: List[str] = Field(default_factory=list, description="Business or technical constraints")
    ambiguities: List[str] = Field(default_factory=list, description="Unclear aspects of the prompt")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made to fill gaps")
    complexity: Literal["simple", "medium", "complex"] = Field(..., description="Estimated complexity")
    has_payments: bool = False
    has_analytics: bool = False
    has_notifications: bool = False
    has_file_uploads: bool = False
