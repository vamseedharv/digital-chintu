"""Small validation helpers shared across Pydantic models that aren't
otherwise related (env-driven Settings, the settings-domain API schemas) —
kept here instead of duplicated so the same rule can't quietly drift
between them.
"""


def validate_short_text(value: str, field_name: str, *, max_length: int = 64) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must not be blank")
    if len(stripped) > max_length:
        raise ValueError(f"{field_name} must be {max_length} characters or fewer")
    return stripped
