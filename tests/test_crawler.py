# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""

from pystockdb.tools.data_crawler import DataCrawler
from pystockdb.tools.fundamentals import Fundamentals
import pytest
import json

SYMBOLS = ['OTCMKTS:ADDDF', 'OTCMKTS:BAYZF', 'OTCMKTS:BMWYY', 'NASDAQ:ADP', 'NASDAQ:BBBY']
SYMBOLS_Y = ['ADDDF', 'BAYZF', 'BMWYY', 'ADP']

@pytest.fixture
def fundamentals_instance():
    return Fundamentals()


@pytest.fixture
def crawler_instance():
    return DataCrawler(True)

@pytest.mark.order(1)
def test_fundamentals(fundamentals_instance):
    """
    Test stock fundamentals crawler
    """
    dividends = fundamentals_instance.get_dividends('ADDDF')
    dividends_dumps = json.dumps(dividends)
    assert dividends_dumps
    brief = fundamentals_instance.get_company_brief('ADS.F')
    brief_dump = json.dumps(brief)
    assert brief_dump
    income = fundamentals_instance.get_income('ADS.F')
    income_dump = json.dumps(income)
    assert income_dump
    recommendation = fundamentals_instance.get_recommendation('ADS.F')
    recommendation_dump = json.dumps(recommendation)
    assert recommendation_dump
    cash_flow = fundamentals_instance.get_cash_flow('ADS.F')
    cash_flow_dump = json.dumps(cash_flow)
    assert cash_flow_dump
    balance = fundamentals_instance.get_balance('ADS.F')
    balance_dump = json.dumps(balance)
    assert balance_dump
    dividends = fundamentals_instance.get_dividends('ADS.F')
    dividends_dumps = json.dumps(dividends)
    assert dividends_dumps
    assert any([income, balance, cash_flow, brief, recommendation, dividends])


@pytest.mark.order(2)
def test_crawler(crawler_instance):
    """
    Test stock data crawler
    """
    price = crawler_instance.get_last_price('ADS.F')
    assert price is not None

    price_stack = crawler_instance.get_last_price_stack(SYMBOLS_Y)
    assert any([symbol in price_stack and price_stack[symbol] for symbol in SYMBOLS_Y])

    ads_day = crawler_instance.get_series('ADS.F', '1d')
    assert ads_day is not None

    dax_day = crawler_instance.get_series('DAX', '1d')
    assert dax_day is not None

    dax_day_stack = crawler_instance.get_series_stack(['DAX'], '1d')
    assert dax_day_stack is not None