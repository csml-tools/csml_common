from pathlib import Path
from typing import Callable
from pydantic import BaseModel
import yaml


def create_yaml_loader[T: BaseModel](type_: type[T]) -> Callable[[str], T]:
    def parser(path: str):
        with Path(path).open() as file:
            return type_.model_validate(yaml.safe_load(file))

    return parser


def range_parser(value: str) -> range:
    parts = value.split("-")

    if len(parts) == 2:
        return range(int(parts[0]), int(parts[1]) + 1)
    elif len(parts) == 1:
        num = int(parts[0])
        return range(num, num + 1)
    else:
        raise ValueError(f"{value} is not a range string expected format like '0-100'")


__all__ = ["create_yaml_loader", "range_parser"]
