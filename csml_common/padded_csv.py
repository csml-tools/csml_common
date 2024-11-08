import re
from typing import Iterable, TextIO, Literal, cast
from itertools import islice
from to_file_like_obj import to_file_like_obj

type HeaderLength = int | Literal["auto"]


def _is_empty_line(line: str) -> bool:
    return line.strip() == "" or re.match(r'^""(,"")*$', line) is not None


def _find_first_csv_line(file: Iterable[str]):
    num_empty = 0

    for line in file:
        if _is_empty_line(line):
            num_empty += 1
        else:
            if num_empty >= 2:
                return line
            num_empty = 0

    raise RuntimeError("Couldn't find first line of csv")


def _from_first_csv_line(file: Iterable[str]):
    yield _find_first_csv_line(file)
    yield from file


def _until_empty_line(file: Iterable[str]):
    for line in file:
        if _is_empty_line(line):
            break
        yield line


def padded_csv_lines(file: TextIO, header_length: HeaderLength):
    return _until_empty_line(
        _from_first_csv_line(file)
        if header_length == "auto"
        else islice(file, header_length, None)
    )


def padded_csv_reader(file: TextIO, header_length: HeaderLength):
    return cast(
        TextIO,
        to_file_like_obj(
            _until_empty_line(
                _from_first_csv_line(file)
                if header_length == "auto"
                else islice(file, header_length, None)
            ),
            base=str,
        ),
    )


__all__ = ["HeaderLength", "padded_csv_lines", "padded_csv_reader"]
