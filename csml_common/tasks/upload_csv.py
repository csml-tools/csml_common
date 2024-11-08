from typing import Any, Optional
from dataclasses import field
from itertools import chain
import pandas as pd
import sqlalchemy.types as types
from sqlalchemy.ext.compiler import compiles

from ralsei import Table
from ralsei.connection import ConnectionEnvironment
from ralsei.task import TaskDef, CreateTableTask

from ..config import CsvSourceGlob
from ..padded_csv import padded_csv_reader


class RawType(types.UserDefinedType):
    def __init__(self, sql: str) -> None:
        self.sql = sql


@compiles(RawType, "sqlite")
def compile_mytype_sqlite(type_: RawType, compiler, **kw):
    return type_.sql


class UploadCsv(TaskDef):
    table: Table
    sources: list[CsvSourceGlob]
    index: Optional[str] = None
    read_csv_args: dict[str, Any] = field(default_factory=dict)

    class Impl(CreateTableTask):
        def prepare(self, this: "UploadCsv"):
            self._prepare_table(this.table)

            self.__sources = this.sources
            self.__index = this.index
            self.__read_csv_args = this.read_csv_args

        def _run(self, conn: ConnectionEnvironment):
            dfs = []

            for source in chain(*(s.expand() for s in self.__sources)):
                with source.path.open() as file:
                    dfs.append(
                        pd.read_csv(
                            padded_csv_reader(file, source.header_length),
                            **self.__read_csv_args,
                        ).rename(source.remap, axis=1)
                    )

            df = pd.concat(dfs, ignore_index=True)

            dtypes = {}
            if self.__index:
                df = df.reset_index(names=self.__index)
                dtypes[self.__index] = RawType("INTEGER PRIMARY KEY")

            df.to_sql(
                self._table.name,
                conn.sqlalchemy,
                schema=self._table.schema,
                index=False,
                dtype=dtypes,
            )


__all__ = ["UploadCsv"]
