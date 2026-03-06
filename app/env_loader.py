from pathlib import Path


def _parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()

    if "=" not in stripped:
        return None

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()

    if not key:
        return None

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]

    return key, value


def load_dotenv(root: Path, filename: str = ".env") -> dict[str, str]:
    env_path = root / filename
    if not env_path.is_file():
        return {}

    loaded: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_env_line(raw_line)
        if parsed is None:
            continue
        key, value = parsed
        loaded[key] = value

    return loaded


def apply_dotenv(root: Path, filename: str = ".env") -> dict[str, str]:
    loaded = load_dotenv(root, filename)
    for key, value in loaded.items():
        if key not in __import__("os").environ:
            __import__("os").environ[key] = value
    return loaded
