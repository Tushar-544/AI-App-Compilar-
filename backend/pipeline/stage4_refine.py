"""Stage 4 — Refinement: resolve cross-layer inconsistencies via LLM."""
import time, logging
from llm.gemini import get_client, PRO
from models.ui_schema import UISchemaModel
from models.api_schema import APISchemaModel
from models.db_schema import DBSchemaModel
from models.auth_schema import AuthSchemaModel

logger = logging.getLogger(__name__)

SYSTEM = """You are a senior architect performing a consistency review across 4 schemas.

Your job:
1. Ensure every UI component's entity exists as a DB table
2. Ensure every UI component's api_endpoint exists as an API endpoint id
3. Ensure every API endpoint's request/response fields exist as DB columns
4. Ensure every role in UI access lists exists in Auth roles
5. Ensure every premium gate in Auth corresponds to a page/feature in UI
6. Ensure all foreign keys in DB match actual table/column names

Fix ALL inconsistencies and return the corrected schemas.
Return ONLY valid JSON with keys: ui_schema, api_schema, db_schema, auth_schema
Keep the same schema structure — only fix inconsistencies.
"""


def run(
    ui: UISchemaModel,
    api: APISchemaModel,
    db: DBSchemaModel,
    auth: AuthSchemaModel,
) -> tuple[UISchemaModel, APISchemaModel, DBSchemaModel, AuthSchemaModel, int, int]:
    client = get_client()
    t0 = time.time()
    retries = 0

    payload = {
        "ui_schema":   ui.model_dump(),
        "api_schema":  api.model_dump(),
        "db_schema":   db.model_dump(),
        "auth_schema": auth.model_dump(),
    }

    import json
    user_msg = f"Review and fix inconsistencies in these schemas:\n\n{json.dumps(payload, indent=2)}"

    for attempt in range(3):
        try:
            data = client.call(SYSTEM, user_msg, PRO, 0.0)
            refined_ui   = UISchemaModel(**data["ui_schema"])
            refined_api  = APISchemaModel(**data["api_schema"])
            refined_db   = DBSchemaModel(**data["db_schema"])
            refined_auth = AuthSchemaModel(**data["auth_schema"])
            ms = int((time.time() - t0) * 1000)
            return refined_ui, refined_api, refined_db, refined_auth, ms, retries
        except Exception as e:
            retries += 1
            logger.warning(f"Stage4 attempt {attempt+1} failed: {e}. Using unrefined schemas.")

    # Fallback: return original schemas if refinement fails
    ms = int((time.time() - t0) * 1000)
    logger.warning("Stage 4 refinement failed — returning original schemas")
    return ui, api, db, auth, ms, retries
