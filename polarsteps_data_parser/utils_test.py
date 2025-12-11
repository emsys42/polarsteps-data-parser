import datetime

import pytest
import utils


def test_parse_date() -> None:  # noqa: D103
    assert utils.parse_date("1752638400.0") == datetime.datetime(2025, 7, 16, 6, 0)
