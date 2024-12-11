from pathlib import Path
from typing import Callable
from pydantic import BaseModel
import yaml


def pydantic_yaml_loader[T: BaseModel](type_: type[T]) -> Callable[[str], T]:
    def parser(path: str):
        with Path(path).open() as file:
            return type_.model_validate(yaml.safe_load(file))

    return parser


__all__ = ["pydantic_yaml_loader"]
