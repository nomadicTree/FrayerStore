import yaml
from pathlib import Path
from .exceptions import YamlLoadError, InvalidYamlStructure
from typing import Any, Mapping


def load_yaml(path: Path) -> Mapping[str, Any]:
    """Safely load a YAML file and return its contents as a mapping."""
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise YamlLoadError(f"YAML parse error in {path}: {e}")

    if data is None:
        raise YamlLoadError(f"YAML file empty: {path}")

    if not isinstance(data, Mapping):
        raise InvalidYamlStructure(
            f"Expected mapping at root of {path}, got {type(data).__name__}"
        )

    return data
