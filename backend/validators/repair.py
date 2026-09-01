"""
Stage 5 — Validation + Repair Engine (CORE of the system).

Two phases:
  Phase A: Pydantic validation (already done by model instantiation)
  Phase B: Cross-layer semantic consistency checks + surgical repair
"""
from models.ui_schema import UISchemaModel
from models.api_schema import APISchemaModel
from models.db_schema import DBSchemaModel
from models.auth_schema import AuthSchemaModel
from models.app_config import ValidationIssue
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def validate_and_repair(
    ui: UISchemaModel,
    api: APISchemaModel,
    db: DBSchemaModel,
    auth: AuthSchemaModel,
) -> Tuple[UISchemaModel, APISchemaModel, DBSchemaModel, AuthSchemaModel, List[ValidationIssue], List[str]]:
    """
    Returns repaired schemas + list of validation issues + repair action log.
    Surgical repairs only — never full retry.
    """
    issues: List[ValidationIssue] = []
    repairs: List[str] = []

    # Build lookup sets
    db_table_names  = {t.name for t in db.tables}
    db_entity_names = {t.entity.lower() for t in db.tables}
    api_endpoint_ids = {e.id for e in api.endpoints}
    auth_roles = set(auth.roles)

    # ── Check 1: UI component entities exist in DB ─────────────────────────
    for page in ui.pages:
        for comp in page.components:
            if comp.entity and comp.entity.lower() not in db_entity_names:
                # Surgical repair: nullify the broken entity ref
                issue = ValidationIssue(
                    severity="error", layer="cross",
                    issue=f"UI component '{comp.id}' references entity '{comp.entity}' not in DB",
                    field=f"ui.pages.{page.id}.components.{comp.id}.entity",
                    auto_repaired=True,
                    repair_action=f"Cleared unknown entity '{comp.entity}' from component '{comp.id}'"
                )
                issues.append(issue)
                repairs.append(issue.repair_action)
                comp.entity = None  # type: ignore[assignment]

    # ── Check 2: UI component api_endpoints exist in API ──────────────────
    for page in ui.pages:
        for comp in page.components:
            if comp.api_endpoint and comp.api_endpoint not in api_endpoint_ids:
                issue = ValidationIssue(
                    severity="warning", layer="cross",
                    issue=f"UI component '{comp.id}' references missing endpoint '{comp.api_endpoint}'",
                    field=f"ui.pages.{page.id}.components.{comp.id}.api_endpoint",
                    auto_repaired=True,
                    repair_action=f"Cleared unknown endpoint ref '{comp.api_endpoint}'"
                )
                issues.append(issue)
                repairs.append(issue.repair_action)
                comp.api_endpoint = None  # type: ignore[assignment]

    # ── Check 3: UI page access roles exist in Auth ────────────────────────
    for page in ui.pages:
        invalid_roles = [r for r in page.access if r not in auth_roles]
        if invalid_roles:
            for r in invalid_roles:
                # Repair: add missing role to auth with minimal permissions
                auth.roles.append(r)
                auth_roles.add(r)
                issue = ValidationIssue(
                    severity="warning", layer="cross",
                    issue=f"Page '{page.id}' references role '{r}' not in Auth",
                    field=f"ui.pages.{page.id}.access",
                    auto_repaired=True,
                    repair_action=f"Added missing role '{r}' to Auth schema"
                )
                issues.append(issue)
                repairs.append(issue.repair_action)

    # ── Check 4: Auth permission_matrix resources map to DB tables ─────────
    for entry in auth.permission_matrix:
        resource = entry.resource.lower().rstrip("s") + "s"  # normalize plural
        if resource not in db_table_names and entry.resource.lower() not in db_table_names:
            issue = ValidationIssue(
                severity="warning", layer="cross",
                issue=f"Auth permission_matrix resource '{entry.resource}' has no matching DB table",
                field=f"auth.permission_matrix.{entry.resource}",
                auto_repaired=False,
            )
            issues.append(issue)

    # ── Check 5: Auth roles reference valid roles ──────────────────────────
    for entry in auth.permission_matrix:
        for role in entry.permissions.keys():
            if role not in auth_roles:
                auth.roles.append(role)
                auth_roles.add(role)
                issue = ValidationIssue(
                    severity="warning", layer="auth",
                    issue=f"Permission matrix references undeclared role '{role}'",
                    auto_repaired=True,
                    repair_action=f"Added undeclared role '{role}' to Auth.roles"
                )
                issues.append(issue)
                repairs.append(issue.repair_action)

    # ── Check 6: DB foreign keys reference real tables ─────────────────────
    for table in db.tables:
        for col in table.columns:
            if col.foreign_key:
                ref_table = col.foreign_key.split(".")[0]
                if ref_table not in db_table_names:
                    issue = ValidationIssue(
                        severity="error", layer="db",
                        issue=f"Column '{table.name}.{col.name}' foreign key '{col.foreign_key}' references unknown table",
                        field=f"db.tables.{table.name}.{col.name}.foreign_key",
                        auto_repaired=True,
                        repair_action=f"Removed invalid foreign key from '{table.name}.{col.name}'"
                    )
                    issues.append(issue)
                    repairs.append(issue.repair_action)
                    col.foreign_key = None  # type: ignore[assignment]

    logger.info(f"Validation complete: {len(issues)} issues, {len(repairs)} auto-repaired")
    return ui, api, db, auth, issues, repairs
