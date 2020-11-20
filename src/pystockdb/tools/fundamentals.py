#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import base64

from uplink import Consumer, Query, get, params, returns


class Fundamentals(Consumer):
    BASE_URL = base64.b64decode(
        'aHR0cDovL3NlY3VyaXRpZXNhcGkuc3RvY2tzNjY2LmNvbS8='
    ).decode('utf-8')

    @returns.json(key='list')
    @params({'hasNumber': 0, 'clientOrder': 3, 'queryNumber': 30})
    @get('/api/search/tickers5')
    def search(self, keys: Query):
        """
        Search for stock by name
        :param keys: stock name or search string
        :return: json data
        """

    def get_ticker_ids(self, symbols: Query):
        """
        Converts symbols to ticker ids
        :param symbols: a list of stock symbols [ETR:ADS,ETR:RIB]
        :return: ticker ids
        """
        chunks = [symbols[x:x + 50] for x in range(0, len(symbols), 50)]
        ticker_dict = {}
        for chunk in chunks:
            data = self.__get_ticker_ids(','.join(chunk))
            for item in data:
                key = '{}:{}'.format(item['sourceExchangeCode'],
                                     item['tickerSymbol'])
                ticker_dict[key] = item['tickerId']
        return ticker_dict

    @returns.json
    @get('/api/stocks/ticker/googleFinancial/tickerIdMapping')
    def __get_ticker_ids(self, symbols: Query):
        """get ticker ids raw. keep in mind that only 50 items are supported"""

    @returns.json
    @get('/api/securities/stock/{ticker_id}/recommendation')
    def get_recommendation(self, ticker_id):
        """
        Returns recommendation data for stock
        :param ticker_id: ticker id
        :return: json data
        """

    @returns.json
    @get('/api/securities/stock/{ticker_id}/statementsV2Detail')
    def get_income_facts(self, ticker_id):
        """
        Returns income data for stock
        :param ticker_id: ticker id
        :return: json data
        """

    @returns.json
    @get('/api/securities/stock/{ticker_id}/incomeAnalysis/crucial')
    def get_income_analysis(self, ticker_id):
        """
        Returns income analysis data for stock
        :param ticker_id: ticker id
        :return: json data
        """

    @returns.json
    @get('/api/securities/stock/{ticker_id}/compBrief')
    def get_company_brief(self, ticker_id):
        """
        Returns company brief data for stock
        :param ticker_id: ticker id
        :return: json data
        """

    def get_cash_flow(self, ticker_id):
        """Returns cash flow of given symbol

        :param ticker_id: ticker id of symbol
        :type ticker_id: str
        :return: cash flow in json format
        :rtype: dict
        """
        return self.get_sheet(ticker_id, 3)

    def get_balance(self, ticker_id):
        """Returns balance of given symbol

        :param ticker_id: ticker id of symbol
        :type ticker_id: str
        :return: balance in json format
        :rtype: dict
        """
        return self.get_sheet(ticker_id, 2)

    def get_income(self, ticker_id):
        """Returns income of given symbol

        :param ticker_id: ticker id of symbol
        :type ticker_id: str
        :return: income in json format
        :rtype: dict
        """
        return self.get_sheet(ticker_id, 1)

    @returns.json
    @get('/api/securities/stock/{ticker_id}/statementsV2Detail')
    def get_sheet(self, ticker_id, sheet_type: Query("type"),
                  query_number: Query('queryNumber') = 300):
        """
        Returns financial sheet(income, balance, cash flow) data for stock
        :param ticker_id: ticker id
        :param sheet_type: income=1, balance=2 and cashflow = 3
        :param query_number:
        :return:
        """
