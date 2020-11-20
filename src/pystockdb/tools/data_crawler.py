#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import yfinance as yf
from pytickersymbols import PyTickerSymbols


class DataCrawler:
    """
    Simple client for financial data
    """

    def __init__(self, skip_fix_symbols=False):
        self.ticker_symbols = None
        if not skip_fix_symbols:
            self.ticker_symbols = PyTickerSymbols()

    def __get_symbol(self, symbol):
        if self.ticker_symbols is not None:
            symbol_fix = self.ticker_symbols.index_to_yahoo_symbol(symbol)
            if symbol_fix is not None:
                symbol = symbol_fix
        return symbol

    def get_series(self, symbol, period='1d', start=None, end=None):
        """
        Creates a series object by given index/stock symbol
        :param symbol: symbol dax, mdax, i7n usw.
        :param period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        :return: series objects or None if no data present
        """
        y_ticker = yf.Ticker(self.__get_symbol(symbol))
        data = y_ticker.history(period=period)
        return DataCrawler.series_to_object(data)

    def get_series_stack(self, symbols, period='1d', start=None, end=None):
        """
        Creates a series object by given index/stock symbol
        :param symbols: list of symbols dax, mdax, i7n usw.
        :param period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        :param start: Download start date string (YYYY-MM-DD) Default is
        1900-01-01
        :param start: Download start date string (YYYY-MM-DD) Default is now
        :return: series objects or None if no data present
        """
        symbols = [self.__get_symbol(symbol) for symbol in symbols]
        symbols_str = ' '.join(symbols)
        if start and end:
            datas = yf.download(tickers=symbols_str, start=start, end=end,
                                group_by='ticker')
        else:
            datas = yf.download(tickers=symbols_str, period=period,
                                group_by='ticker')
        data_dict = {}
        for symbol in symbols:
            if len(symbols) > 1:
                data_dict[symbol] = DataCrawler.series_to_object(
                    datas[symbol].dropna()
                )
            else:
                data_dict[symbol] = DataCrawler.series_to_object(
                    datas.dropna()
                )
        return data_dict

    @staticmethod
    def series_to_object(data):
        """
        Transforms the json response to sqlalchemy object.
        :param data: json response
        :return: sqlalchemy object
        """
        series_list = []

        for timestamp, series in data.iterrows():
            series_list.append(
                {
                    'open': series.Open,
                    'close': series.Close,
                    'high': series.High,
                    'low': series.Low,
                    'volume': int(series.Volume),
                    'date': timestamp.to_pydatetime()
                }
            )
        return series_list

    def get_last_price(self, stock_object):
        """

        :param stock_object:
        :return:
        """
        symbol = self.__get_symbol(stock_object)
        data = self.get_series(symbol, '1d')
        return data

    def get_last_price_stack(self, symbols):
        """

        :param stock_object:
        :return:
        """
        datas = self.get_series_stack(symbols, '1d')
        return datas
