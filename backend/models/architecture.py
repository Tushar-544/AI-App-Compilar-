from pydantic import BaseModel, Field
from typing import List, Literal


class EntityRelationship(BaseModel):
    from_entity: str
    to_entity: str
    relation_type: Literal["has_one", "has_many", "belongs_to", "many_to_many"]
    foreign_key: str


class NavigationItem(BaseModel):
    id: str
    label: str
    route: str
    icon: str
    roles: List[str]
    is_premium: bool = False


class BusinessFlow(BaseModel):
    name: str
    description: str
    steps: List[str]
    entities_involved: List[str]


class ArchitectureModel(BaseModel):
    app_name: str
    pages: List[str]
    navigation: List[NavigationItem]
    auth_strategy: str
    entity_relationships: List[EntityRelationship]
    business_flows: List[BusinessFlow]
    integrations: List[str]
    tech_notes: List[str]
