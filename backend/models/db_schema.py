from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class DBColumn(BaseModel):
    name: str
    type: str  # UUID, VARCHAR(255), INTEGER, BOOLEAN, TIMESTAMP, TEXT, DECIMAL(10,2)
    nullable: bool = False
    primary_key: bool = False
    unique: bool = False
    foreign_key: Optional[str] = None   # "table_name.column_name"
    default_value: Optional[str] = None # "NOW()", "gen_random_uuid()"
    auto_generated: bool = False


class DBTable(BaseModel):
    name: str    # snake_case plural  e.g. contacts
    entity: str = ""  # PascalCase  e.g. Contact — auto-derived if empty
    columns: List[DBColumn]
    indexes: List[str] = Field(default_factory=list)
    soft_delete: bool = True  # adds deleted_at column

    def model_post_init(self, __context) -> None:
        if not self.entity:
            # Derive PascalCase entity from table name
            self.entity = self.name.replace("_", " ").title().replace(" ", "")


class DBSchemaModel(BaseModel):
    tables: List[DBTable]
    db_type: Literal["PostgreSQL", "MySQL", "SQLite"] = "PostgreSQL"
    enable_row_level_security: bool = True
