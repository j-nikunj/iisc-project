import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import yaml


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_yaml_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def coalesce(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return value
    return None


def resolve_config_path(config_path: Optional[str], value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    path = Path(value)
    if path.is_absolute() or not config_path:
        return str(path)
    base_dir = Path(config_path).parent
    return str(base_dir / path)
