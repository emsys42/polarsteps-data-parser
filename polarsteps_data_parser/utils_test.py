import pytest

import utils
import datetime

def test_parse_date():
    assert utils.parse_date("1752638400.0") == datetime.datetime(2025, 7, 16, 6, 0)