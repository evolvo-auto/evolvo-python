def build_conventional_commit_message(commit_type: str, scope: str, description: str) -> str:
    commit_type_value = commit_type.strip()
    scope_value = scope.strip()
    description_value = description.strip()

    if not commit_type_value:
        raise ValueError("commit type must be non-empty")
    if not scope_value:
        raise ValueError("scope must be non-empty")
    if not description_value:
        raise ValueError("description must be non-empty")
    if description_value != description_value.lower():
        raise ValueError("description must be lowercase")
    if description_value.endswith("."):
        raise ValueError("description must not end with a period")

    return f"{commit_type_value}({scope_value}): {description_value}"
