from pathlib import Path
from typing import Iterable
from pydantic import BaseModel
from glob import iglob

from .padded_csv import HeaderLength


class CsvSource(BaseModel):
    path: Path
    header_length: HeaderLength
    remap: dict[str, str] = {}


class CsvSourceGlob(BaseModel):
    glob: str
    header_length: HeaderLength
    remap: dict[str, str] = {}

    def expand(self) -> Iterable[CsvSource]:
        for path in iglob(self.glob, recursive=True):
            yield CsvSource(
                path=Path(path), header_length=self.header_length, remap=self.remap
            )


__all__ = ["CsvSource", "CsvSourceGlob"]
