#!/usr/bin/env python3
# encoding=utf-8
"""
@author:xli3
@time:3/12/2024 2:16 PM
@file:conftest.py
"""

import pytest
import sys


from utils.log_record import log


@pytest.fixture(scope='function', autouse=True)
def fixture_log():
    log.info('-' * 80)
    log.info('-' * 30 + ' Test starts ' + '-' * 37)
    log.info('-' * 80)
    yield
    log.info('-' * 80)
    log.info('-' * 30 + ' Test ends ' + '-' * 39)
    log.info('-' * 80)


if __name__ == "__main__":
    pass
