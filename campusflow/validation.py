def validate_title(raw):
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("Title cannot be blank")
    return raw.strip()

def validate_category(raw):
    if not isinstance(raw, str):
        raise ValueError("Invalid category")
    canon = {"network": "Network", "hardware": "Hardware", "software": "Software", "other": "Other"}
    key = raw.strip().casefold()
    if key not in canon:
        raise ValueError("Category must be Network, Hardware, Software or Other")
    return canon[key]

def validate_urgency(raw):
    if not isinstance(raw, str):
        raise ValueError("Invalid urgency")
    key = raw.strip().casefold()
    if key not in ("low", "medium", "high"):
        raise ValueError("Urgency must be low, medium or high")
    return key

def validate_affected_users(raw):
    if isinstance(raw, bool):
        raise ValueError("affected_users cannot be bool")
    if isinstance(raw, str):
        raise ValueError("affected_users must be integer")
    if isinstance(raw, float):
        raise ValueError("affected_users must be integer, not float")
    if not isinstance(raw, int):
        raise ValueError("affected_users must be integer")
    if raw <= 0:
        raise ValueError("affected_users must be positive")
    return raw
