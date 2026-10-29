from pathlib import Path

import pytest

from expenses import load_expenses, parse_line, total_by_category

REAL_FILE = Path(__file__).resolve().parent / "data" / "expenses.csv"

ROWS = [
    ("2026-09-23;electronics;1290.00;wireless keyboard", "electronics", 1290.0),
    ("2026-09-23;bakery;145.00;croissants and bread", "bakery", 145.0),
    ("2026-09-24;books;380.00;programming notebook", "books", 380.0),
    ("2026-09-25;groceries;735.00;fruit and vegetables", "groceries", 735.0),
    ("2026-09-29;electronics;2450.00;headphones", "electronics", 2450.0),
]
EXPECTED_TOTALS = {
    "electronics": 3740.0, "bakery": 145.0, "books": 380.0, "cinema": 420.0,
    "groceries": 1195.0, "transport": 68.0, "games": 560.0, "pharmacy": 215.0,
    "cafe": 310.0, "clothing": 890.0, "stationery": 175.0,
}
EXPECTED_RECORDS = 13


def test_parse_line_valid():
    record = parse_line("2026-09-21;food;85.50;lunch")
    assert record["category"] == "food"
    assert record["amount"] == 85.5


def test_parse_line_returns_full_record():
    assert parse_line("2026-09-21;food;85.50;lunch") == {
        "date": "2026-09-21", "category": "food", "amount": 85.5, "comment": "lunch"}


def test_parse_line_strips_spaces_and_newline():
    record = parse_line(" 2026-09-21 ; food ; 85.50 ; lunch \n")
    assert record["category"] == "food"
    assert record["comment"] == "lunch"


def test_parse_line_bad_amount():
    with pytest.raises(ValueError):
        parse_line("2026-09-21;food;abc;lunch")


@pytest.mark.parametrize("line", [
    "2026-09-21;food;85.50",
    "2026-09-21;food;85.50;lunch;extra",
    "",
])
def test_parse_line_wrong_field_count(line):
    with pytest.raises(ValueError):
        parse_line(line)


@pytest.mark.parametrize("line", [
    "21.09.2026;food;85.50;lunch",
    "2026-09-21;food;nan;lunch",
])
def test_parse_line_other_bad_values(line):
    with pytest.raises(ValueError):
        parse_line(line)


@pytest.mark.parametrize("line, category, amount", ROWS)
def test_parse_line_real_rows(line, category, amount):
    record = parse_line(line)
    assert record["category"] == category
    assert record["amount"] == amount


def make_file(tmp_path):
    path = tmp_path / "expenses.csv"
    path.write_text(
        "# date;category;amount;comment\n"
        "2026-09-21;food;85.50;lunch\n"
        "\n"
        "2026-09-22;food;14.50;coffee\n",
        encoding="utf-8",
    )
    return path


def test_load_expenses_skips_comments_and_empty(tmp_path):
    records = load_expenses(make_file(tmp_path))
    assert len(records) == 2
    assert records[0]["comment"] == "lunch"


def test_total_by_category(tmp_path):
    path = tmp_path / "expenses.csv"
    path.write_text(
        "# date;category;amount;comment\n"
        "2026-09-21;food;85.50;lunch\n"
        "\n"
        "2026-09-22;food;14.50;coffee\n",
        encoding="utf-8",
    )
    totals = total_by_category(load_expenses(path))
    assert totals == {"food": 100.0}


def test_total_by_category_rounds_to_two_digits():
    records = [{"category": "a", "amount": 0.1}, {"category": "a", "amount": 0.2}]
    assert total_by_category(records) == {"a": 0.3}


def test_load_expenses_bad_row_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("2026-09-21;food;abc;lunch\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_expenses(path)


def test_total_by_category_on_real_file():
    totals = total_by_category(load_expenses(REAL_FILE))
    assert totals == EXPECTED_TOTALS


def test_load_expenses_skips_header_line(tmp_path):
    path = tmp_path / "expenses.csv"
    path.write_text("date;category;amount;note\n2026-09-23;books;380.00;notebook\n", encoding="utf-8")
    records = load_expenses(path)
    assert len(records) == 1
    assert records[0]["category"] == "books"


def test_load_expenses_real_file_record_count():
    assert len(load_expenses(REAL_FILE)) == EXPECTED_RECORDS