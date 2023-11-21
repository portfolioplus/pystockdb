#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from pandas import Timestamp
import yfinance as yf
from typing import Optional, Dict, Any, Union


class Fundamentals:

    def __convert_timestamps(obj):
        if isinstance(obj, dict):
            return {Fundamentals.__convert_timestamps(k): Fundamentals.__convert_timestamps(v) for k, v in obj.items()}
        elif isinstance(obj, Timestamp):
            return str(obj)
        else:
            return obj

    def _get_attribute(self, stock: yf.Ticker, attribute_name: str, as_dict: bool = False) -> Optional[Any]:
        """
        Helper function to retrieve a specific attribute from a yfinance Ticker object.

        Args:
            stock (yf.Ticker): The yfinance Ticker object.
            attribute_name (str): The name of the attribute to retrieve.
           as_dict (bool): If True, attempt to convert the attribute to a dictionary.

        Returns:
            Optional[Any]: The value of the attribute if successful, otherwise None.
        """
        try:
            attribute_value = getattr(stock, attribute_name)
            return_val = attribute_value.to_dict() if as_dict and hasattr(attribute_value, 'to_dict') else attribute_value
            if isinstance(return_val, dict):
                # Convert timestamp keys to strings
                return_val = Fundamentals.__convert_timestamps(return_val)
            return return_val
        except Exception as e:
            print(f"Error fetching {attribute_name} data: {e}")
            return None

    def get_recommendation(self, ticker_id: str) -> Dict[str, Union[Optional[Any], Optional[Any], Optional[Any]]]:
        """
        Returns recommendation data for a stock.

        Args:
            ticker_id (str): The ticker id of the stock.

        Returns:
            Dict[str, Union[Optional[Any], Optional[Any], Optional[Any]]]: The recommendation data.
        """
        stock = yf.Ticker(ticker_id)
        recommendations = self._get_attribute(stock, 'recommendations', True)
        analyst_price_target = self._get_attribute(stock, 'analyst_price_target', True)
        recommendations_summary = self._get_attribute(stock, 'recommendations_summary', True)

        return {
            "recommendations": recommendations,
            "analyst_price_target": analyst_price_target,
            "recommendations_summary": recommendations_summary
        }

    def get_dividends(self, ticker_id: str) -> Dict[str, Union[Optional[Any], Optional[Any], Optional[Any], Optional[Any]]]:
        """
        Returns dividend data for a stock.

        Args:
            ticker_id (str): The ticker id of the stock.

        Returns:
            Dict[str, Union[Optional[Any], Optional[Any], Optional[Any], Optional[Any]]]: The dividend data.
        """
        stock = yf.Ticker(ticker_id)
        dividends = self._get_attribute(stock, 'dividends', True)
        earnings_dates = self._get_attribute(stock, 'earnings_dates', True)
        earnings_forecasts = self._get_attribute(stock, 'earnings_forecasts', True)
        earnings_trend = self._get_attribute(stock, 'earnings_trend', True)

        return {
            "dividends": dividends,
            "earnings_dates": earnings_dates,
            "earnings_forecasts": earnings_forecasts,
            "earnings_trend": earnings_trend
        }

    def get_company_brief(self, ticker_id: str) -> Dict[str, Optional[Any]]:
        """
        Returns company brief data for a stock.

        Args:
            ticker_id (str): The ticker id of the stock.

        Returns:
            Dict[str, Optional[Any]]: The company brief data.
        """
        stock = yf.Ticker(ticker_id)
        info = self._get_attribute(stock, 'info')

        return {
            "info": info
        }

    def get_cash_flow(self, ticker_id: str) -> Dict[str, Union[Optional[Any], Optional[Any]]]:
        """
        Returns cash flow data for a stock.

        Args:
            ticker_id (str): The ticker id of the stock.

        Returns:
            Dict[str, Union[Optional[Any], Optional[Any]]]: The cash flow data.
        """
        stock = yf.Ticker(ticker_id)
        cash_flow = self._get_attribute(stock, 'cashflow', True)
        cash_flow_quarterly = self._get_attribute(stock, 'quarterly_cashflow', True)

        return {
            "cash_flow": cash_flow,
            "cash_flow_quarterly": cash_flow_quarterly
        }

    def get_balance(self, ticker_id: str) -> Dict[str, Union[Optional[Any], Optional[Any]]]:
        """
        Returns balance data for a stock.

        Args:
            ticker_id (str): The ticker id of the stock.

        Returns:
            Dict[str, Union[Optional[Any], Optional[Any]]]: The balance data.
        """
        stock = yf.Ticker(ticker_id)
        balancesheet = self._get_attribute(stock, 'balancesheet', True)
        quarterly_balancesheet = self._get_attribute(stock, 'quarterly_balancesheet', True)

        return {
            "balancesheet": balancesheet,
            "quarterly_balancesheet": quarterly_balancesheet
        }

    def get_income(self, ticker_id: str) -> Dict[str, Union[Optional[Any], Optional[Any]]]:
        """
        Returns income data for a stock.

        Args:
            ticker_id (str): The ticker id of the stock.

        Returns:
            Dict[str, Union[Optional[Any], Optional[Any]]]: The income data.
        """
        stock = yf.Ticker(ticker_id)
        income = self._get_attribute(stock, 'income_stmt', True)
        income_quarterly = self._get_attribute(stock, 'quarterly_income_stmt', True)

        return {
            "income": income,
            "income_quarterly": income_quarterly
        }
