from typing import Any, Optional
from dataclasses import field
from itertools import chain
import pandas as pd
import sqlalchemy.types as types
from sqlalchemy.ext.compiler import compiles

from ralsei import Table
from ralsei.jinja import SqlEnvironment
from ralsei.connection import ConnectionEnvironment
from ralsei.task import TaskDef, Task, TableOutput
from ralsei.jinja.globals import autoincrement_primary_key

from ..config import CsvSourceGlob
from ..padded_csv import padded_csv_reader


class RawType(types.UserDefinedType):
    def __init__(self, sql: str) -> None:
        self.sql = sql


@compiles(RawType)
def compile_mytype_sqlite(type_: RawType, compiler, **kw):
    return type_.sql


class UploadCsv(TaskDef):
    table: Table
    sources: list[CsvSourceGlob]
    index: Optional[str] = None
    read_csv_args: dict[str, Any] = field(default_factory=dict)

    class Impl(Task[TableOutput]):
        def __init__(self, this: "UploadCsv", env: SqlEnvironment) -> None:
            self.output = TableOutput(env, this.table)

            self.__sources = this.sources
            self.__index = this.index
            self.__read_csv_args = this.read_csv_args
            self.__primary_key_str = env.resolve(
                autoincrement_primary_key(env, this.table)
            ).to_sql(env)

        def run(self, conn: ConnectionEnvironment):
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
                dtypes[self.__index] = RawType(self.__primary_key_str)

            df.to_sql(
                self.output.table.name,
                conn.sqlalchemy,
                schema=self.output.table.schema,
                index=False,
                dtype=dtypes,
            )
            conn.commit()


__all__ = ["UploadCsv"]
