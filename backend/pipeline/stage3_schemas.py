"""Stage 3 — Combined schema generation (UI, API, DB, Auth) in a single request for speed."""
import time, logging, json
from llm.gemini import get_client, PRO
from models.intent import IntentModel
from models.architecture import ArchitectureModel
from models.ui_schema import UISchemaModel
from models.api_schema import APISchemaModel
from models.db_schema import DBSchemaModel
from models.auth_schema import AuthSchemaModel

logger = logging.getLogger(__name__)

MASTER_SYS = """You are a full-stack architect. Generate the complete technical schemas (UI, API, DB, Auth) for the application based on the provided intent and architecture.

Return ONLY a single valid JSON object with these 4 keys: "ui", "api", "db", "auth".

1. "ui": {
   "pages": [{"id":"string","title":"string","route":"string","layout":"string","access":["role"],"components":[{"id":"string","type":"string","label":"string","entity":"string","api_endpoint":"string","props":{}}]}],
   "theme":"dark|light","navigation_type":"sidebar|topbar","brand_name":"string"
}
2. "api": {
   "base_path":"/api/v1","endpoints":[{"id":"string","method":"GET|POST|PUT|DELETE","path":"string","description":"string","auth_required":boolean,"roles":["string"]}]
}
3. "db": {
   "db_type":"PostgreSQL","tables":[{"name":"string","columns":[{"name":"string","type":"string","primary_key":boolean,"foreign_key":"table.column|null"}]}]
}
4. "auth": {
   "strategy":"JWT","roles":["string"],"default_role":"string","permission_matrix":[{"resource":"string","permissions":{"role":"CRUD_string"}}]
}

Rules:
- Ensure cross-layer consistency: UI components must point to existing API endpoints. API endpoints must reflect DB tables.
- Use the entity names and relationships defined in the Intent and Architecture.
- Generate CRUD endpoints and tables for every primary entity.
"""

def run(
    intent: IntentModel,
    arch: ArchitectureModel,
) -> tuple[UISchemaModel, APISchemaModel, DBSchemaModel, AuthSchemaModel, int, int]:
    """Generates all 4 schemas in a single LLM call to save time and avoid rate limits."""
    t0 = time.time()
    client = get_client()
    
    ctx = f"Intent:\n{intent.model_dump_json()}\n\nArchitecture:\n{arch.model_dump_json()}"
    
    max_retries = 3
    last_err = None
    retries_used = 0
    for attempt in range(1, max_retries + 1):
        try:
            data = client.call(
                MASTER_SYS,
                f"Generate the full technical manifest (UI, API, DB, Auth) for this app:\n{ctx}",
                PRO,
                0.0
            )
            ui   = UISchemaModel(**data["ui"])
            api  = APISchemaModel(**data["api"])
            db   = DBSchemaModel(**data["db"])
            auth = AuthSchemaModel(**data["auth"])
            break
        except Exception as e:
            last_err = e
            retries_used = attempt
            logger.warning(f"Stage 3 attempt {attempt} failed: {e}")
            if attempt == max_retries:
                raise
            import time
            time.sleep(2 * attempt)

    ms = int((time.time() - t0) * 1000)
    return ui, api, db, auth, ms, retries_used
