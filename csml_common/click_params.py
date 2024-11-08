import click
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel
import yaml


class YamlParamType(click.ParamType):
    def __init__(self, type_: type[BaseModel]) -> None:
        self.__type = type_
        self.name = type_.__name__

    def __load(self, path: Path):
        with path.open() as file:
            return self.__type.model_validate(yaml.safe_load(file))

    def convert(
        self, value: Any, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> Any:
        if isinstance(value, self.__type):
            return value
        elif isinstance(value, str):
            return self.__load(Path(value))
        elif isinstance(value, Path):
            return self.__load(value)
        else:
            self.fail(f"Unexpected type: {type(value)}", param, ctx)


__all__ = ["YamlParamType"]
