import pytest

from agents_playground.sys.logger import LOG_TABLE_NONUNIFORM_ERR, LogTableError, TableStats, _build_table_format, _determine_table_stats, _format_table_rows, _stringify


@pytest.fixture
def nonuniform_table() -> list[list]:
    return [
        [],
        [1, 'abc'],
        [1, 2, 3]
    ]

@pytest.fixture
def uniform_table() -> list[list]:
    return [
        ['', '', '', '' , '', '', '', '', ''],
        ['', '', '', '' , '', '', '', '', ''],
        ['', '', '', '' , '', '', '', '', ''],
        ['a', 'aa', 'aaa', 'aaaa', 'aaaaa', 'aaaaaa', 'aaaaaaa', 'aaaaaaaa', 'aaaaaaaaa'],
        ['', '', '', '' , '', '', '', '', ''],
        ['', '', '', '' , '', '', '', '', ''],
        ['', '', '', '' , '', '', '', '', ''],
        ['', '', '', '' , '', '', '', '', ''],
        ['', '', '', '' , '', '', '', '', ''],
        ['', '', '', '' , '', '', '', '', '']
    ]

@pytest.fixture
def assorted_table() -> list[list]:
    return [
        [1, 2, 3, 4],
        ["aaa", "aaaa", "aa", "aaaa"],
        [True, False, 0, None],
        [17, 'abcdefg', 14.2, ''],
    ]

class TestLogTable:
    def test_uniform_table(self, uniform_table) -> None:
        stats: TableStats = _determine_table_stats(uniform_table)
        assert stats.num_cols == 9
        assert len(stats.col_widths) == stats.num_cols
        for col, width in enumerate(stats.col_widths):
            assert col + 1 == width

    def test_nonuniform_table(self, nonuniform_table: list[list]) -> None:
        with pytest.raises(LogTableError) as e:
            _determine_table_stats(nonuniform_table)
        assert LOG_TABLE_NONUNIFORM_ERR in str(e.value)

    def test_build_table(self, assorted_table) -> None:
        separator = " | "
        rows_of_strings: list[list[str]] = _stringify(assorted_table)
        header = ["A", "B", "C", "D"]
        table_stats: TableStats = _determine_table_stats([header] + rows_of_strings, separator)
        formatter: str = _build_table_format(table_stats.col_widths, separator)
        formatted_rows: list[str] = _format_table_rows(table_stats, formatter, header, rows_of_strings)
        print("\n".join(formatted_rows))
        assert False