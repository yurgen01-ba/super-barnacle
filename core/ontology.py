ONTOLOGY_TYPES = [
    "actor", "role", "business_object", "data_object", "process", "workflow",
    "module", "integration", "external_system", "api", "database", "event",
    "document", "screen", "business_rule", "risk", "metric", "report",
    "configuration", "permission", "status", "currency", "country", "product",
    "technical_object", "unknown",
]

ONTOLOGY_TYPE_DESCRIPTIONS = {
    "actor": "Human or organization participating in the business process.",
    "role": "Functional responsibility or permission-bearing role.",
    "business_object": "Core domain object manipulated by the system.",
    "data_object": "Data structure, field group, or persisted information object.",
    "process": "Business process or operational flow.",
    "workflow": "Step-by-step workflow or lifecycle.",
    "module": "Application module, feature area, or product component.",
    "integration": "Integration with an external/internal system or provider.",
    "external_system": "System outside the product boundary.",
    "api": "API, endpoint, webhook, or technical interface.",
    "database": "Database, table, storage, or persistence layer.",
    "event": "Domain event, system event, notification, or trigger.",
    "document": "Document, page, report, statement, file, or artifact.",
    "screen": "UI screen, form, modal, tab, page, or interface view.",
    "business_rule": "Business rule, validation rule, policy, or constraint.",
    "risk": "Risk, issue, blocker, defect, or potential failure mode.",
    "metric": "Metric, KPI, score, rate, balance, amount, or calculated value.",
    "report": "Report, dashboard, export, or analytical view.",
    "configuration": "Configurable setting, status mapping, toggle, or system setup.",
    "permission": "Permission, access rule, privilege, or authorization concept.",
    "status": "State/status in a lifecycle.",
    "currency": "Currency or monetary unit.",
    "country": "Country, region, jurisdiction, or market.",
    "product": "Named product, sub-product, or offering.",
    "technical_object": "Technical object that does not fit API/database/integration yet.",
    "unknown": "Unknown or not classified yet.",
}

HEURISTIC_TYPE_HINTS = {
    "merchant": "actor", "borrower": "actor", "client": "actor", "customer": "actor",
    "underwriter": "actor", "funder": "actor", "syndicator": "actor",
    "referrer": "actor", "isa": "actor", "iso": "actor",
    "advance": "business_object", "draw": "business_object", "payment": "business_object",
    "fee": "business_object", "invoice": "business_object", "contact": "business_object",
    "worksheet": "module",
    "payback": "process", "funding": "process", "underwriting": "process",
    "collections": "process", "collection": "process", "onboarding": "process",
    "reconciliation": "process",
    "plaid": "integration", "stripe": "integration", "equifax": "integration",
    "jira": "external_system", "confluence": "external_system", "slack": "external_system",
    "api": "api", "webhook": "api", "endpoint": "api",
    "screen": "screen", "tab": "screen", "modal": "screen", "form": "screen",
    "report": "report", "dashboard": "report", "export": "report",
    "status": "status", "state": "status",
    "currency": "currency", "country": "country",
    "loci": "product", "loc": "product", "rdmetr": "product",
}


def normalize_ontology_type(value: str | None) -> str:
    value = (value or "unknown").strip().lower().replace(" ", "_").replace("-", "_")
    return value if value in ONTOLOGY_TYPES else "unknown"


def infer_ontology_type_heuristic(name: str, entity_type: str | None = None, facts: list[dict] | None = None):
    name_l = (name or "").lower()
    entity_type_l = (entity_type or "").lower()
    facts = facts or []

    for hint, ontology_type in HEURISTIC_TYPE_HINTS.items():
        if hint in name_l:
            return ontology_type, 0.86, f"name contains '{hint}'"

    mapped_types = {
        "role": "actor",
        "business_object": "business_object",
        "product": "product",
        "integration": "integration",
        "process": "process",
        "technical_object": "technical_object",
        "ui": "screen",
    }

    if entity_type_l in mapped_types:
        return mapped_types[entity_type_l], 0.74, f"mapped from entity_type {entity_type_l}"

    predicates = " ".join(str(f.get("predicate") or "").lower() for f in facts)
    fact_types = " ".join(str(f.get("fact_type") or "").lower() for f in facts)

    if "integrates_with" in predicates or "integration" in fact_types:
        return "integration", 0.72, "relationship/fact suggests integration"
    if "approved_by" in predicates or "created_by" in predicates:
        return "actor", 0.64, "approval/creation relation suggests actor"
    if "process" in fact_types or "workflow" in fact_types:
        return "process", 0.68, "fact type suggests process"
    if "api" in fact_types:
        return "api", 0.70, "fact type suggests api"
    if "ui_screen" in fact_types:
        return "screen", 0.70, "fact type suggests screen"
    if "business_rule" in fact_types:
        return "business_rule", 0.58, "fact type suggests business rule"

    return "unknown", 0.30, "no strong heuristic match"

