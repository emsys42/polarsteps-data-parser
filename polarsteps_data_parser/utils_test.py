import datetime

import pytest
import utils


def test_parse_date() -> None:  # noqa: D103
    assert utils.parse_date("1752638400.0") == datetime.datetime(2025, 7, 16, 6, 0)

def test__decode_step_filter__single_page() -> None:  # noqa: D103
    assert utils.decode_step_filter("1") == [1]
    assert utils.decode_step_filter("15") == [15]

def test__decode_step_filter__negative_page__raises_error() -> None:  # noqa: D103
    with pytest.raises(ValueError):
        utils.decode_step_filter("1,-2")

def test__decode_step_filter__page_zero__raises_error() -> None:  # noqa: D103
    with pytest.raises(ValueError):
        utils.decode_step_filter("0")

def test__decode_step_filter__list_of_pages__output_is_sorted() -> None:  # noqa: D103
    assert utils.decode_step_filter("2,3,4") == [2,3,4]
    assert utils.decode_step_filter("3,4,2") == [2,3,4]

def test__decode_step_filter__list_of_pages__no_duplicates() -> None:  # noqa: D103
    assert utils.decode_step_filter("2,3,4,4") == [2,3,4]
    assert utils.decode_step_filter("3,2,3,4,2") == [2,3,4]

def test__decode_step_filter__ranges_of_pages() -> None:  # noqa: D103
    assert utils.decode_step_filter("3-5") == [3,4,5]
    assert utils.decode_step_filter("63-64,3-4") == [3,4,63,64]

def test__decode_step_filter__invalid_range__raises_error() -> None:  # noqa: D103
    with pytest.raises(ValueError):
        utils.decode_step_filter("5-3")

def test__decode_step_filter__invalid_syntax__raises_error() -> None:  # noqa: D103
    with pytest.raises(ValueError):
        utils.decode_step_filter("1-3-7")

def test__decode_step_filter__combinations() -> None:  # noqa: D103
    assert utils.decode_step_filter("3-5,8") == [3,4,5,8]
    assert utils.decode_step_filter("7,55-56,1") == [1,7,55,56]
