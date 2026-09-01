from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class APIField(BaseModel):
    name: str
    type: str  # string, integer, float, boolean, uuid, email, url, datetime, date, array, object, enum, file
    required: bool = True
    description: Optional[str] = None
    enum_values: Optional[List[str]] = None
    is_array: bool = False


class APIEndpoint(BaseModel):
    id: str                  # unique snake_case id
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str                # e.g. /api/v1/contacts
    description: str
    tags: List[str] = Field(default_factory=list)  # entity tags
    request_body: List[APIField] = Field(default_factory=list)
    query_params: List[APIField] = Field(default_factory=list)
    path_params: List[APIField] = Field(default_factory=list)
    response_fields: List[APIField] = Field(default_factory=list)
    auth_required: bool = True
    roles: List[str] = Field(default_factory=list)
    rate_limited: bool = False
    paginated: bool = False


class APISchemaModel(BaseModel):
    base_path: str = "/api/v1"
    endpoints: List[APIEndpoint]
    auth_base_path: str = "/api/auth"
    api_version: str = "v1"
