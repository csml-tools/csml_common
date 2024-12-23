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


class RangeParamType(click.ParamType):
    name = "range"

    def convert(
        self, value: Any, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> Any:
        if isinstance(value, range):
            return range
        elif isinstance(value, str):
            parts = value.split("-")

            if len(parts) == 2:
                return range(int(parts[0]), int(parts[1]) + 1)
            elif len(parts) == 1:
                num = int(parts[0])
                return range(num, num + 1)
            else:
                self.fail(
                    f"{value} is not a range string expected format like '0-100'",
                    param,
                    ctx,
                )
        else:
            self.fail("Must be str or range", param, ctx)


range_param_type = RangeParamType()


__all__ = ["YamlParamType", "range_param_type"]
