#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import datetime
import hashlib
import json
import logging
from datetime import timedelta

from pony.orm import commit, db_session, select

from pystockdb.db.schema.stocks import (
    Data,
    DataItem,
    Item,
    Price,
    PriceItem,
    Tag,
    Symbol,
)
from pystockdb.tools.base import DBBase
from pystockdb.tools.fundamentals import Fundamentals
from pystockdb.tools import ALL_SYMBOLS


class UpdateDataBaseStocks(DBBase):
    """
    Update Tool for autotrader database
    """

    def __init__(self, arguments: dict, logger: logging.Logger):
        super(UpdateDataBaseStocks, self).__init__(arguments, logger)
        self.logger = logger
        self.db_args = arguments['db_args']
        self.symbols = arguments['symbols']
        self.history = arguments.get('max_history', 5)

    def build(self):
        """
        Starts the update process
        :return: nothing
        """
        if self.arguments.get('prices', False):
            self.update_prices()
        if self.arguments.get('fundamentals', False):
            self.update_fundamentals()
        return 0

    @db_session
    def update_prices(self):
        """Update all prices of stocks
        """
        # get symbols
        prices = list(select((max(p.date), p.symbol) for p in Price))
        if ALL_SYMBOLS not in self.symbols:
            price_filtered = []
            for symbol in set(self.symbols):
                if len(prices) == 0:
                    # download initial data
                    price_filtered.append(
                        [
                            datetime.datetime.now()
                            - timedelta(days=365 * self.history),
                            Symbol.get(name=symbol),
                        ]
                    )
                else:
                    for price in prices:
                        if symbol == price[1].name:
                            price_filtered.append(price)
            prices = price_filtered
        # create update dict
        update = {}
        for price in prices:
            max_date = (price[0] + timedelta(days=1)).strftime('%Y-%m-%d')
            if max_date in update:
                update[max_date].append(price[1])
            else:
                update[max_date] = [price[1]]
        # update
        for key in update:
            start = datetime.datetime.strptime(key, '%Y-%m-%d')
            end = datetime.datetime.now()
            if start.date() >= end.date():
                continue
            self.download_historicals(
                update[key],
                start=start.strftime('%Y-%m-%d'),
                end=end.strftime('%Y-%m-%d'),
            )
        commit()

    @db_session
    def update_fundamentals(self):
        """Updates all fundamentals of stocks
        """
        # At the moment Fundamental client supports only usd symbols
        stocks = list(
            select(
                (pit.stock, sym.name)
                for pit in PriceItem
                for sym in pit.symbols
                if (Tag.GOG in sym.item.tags.name)
                and (Tag.USD in sym.item.tags.name)
            )
        )
        # filter specific stocks if not all
        if ALL_SYMBOLS not in self.symbols:
            stocks_filtered = []
            for stock in stocks:
                for sym in self.symbols:
                    for st_sym in stock[0].price_item.symbols:
                        if sym == st_sym.name:
                            stocks_filtered.append(stock)
            stocks = stocks_filtered
        # create list of google symbols
        gog_syms = [sto[1] for sto in stocks]
        fundamentals = Fundamentals(base_url=Fundamentals.BASE_URL)
        tickers = fundamentals.get_ticker_ids(gog_syms)
        for ticker in tickers:
            self.logger.info(
                'Download fundamentals for {}'.format(tickers[ticker])
            )
            stock = [sto[0] for sto in stocks if sto[1] == ticker]
            if len(stock) != 1:
                self.logger.warning(
                    'Can not download fundamentals for {}'.format(ticker)
                )
                continue
            stock = stock[0]
            ica = fundamentals.get_income_analysis(tickers[ticker])
            ifc = fundamentals.get_income_facts(tickers[ticker])
            rec = fundamentals.get_recommendation(tickers[ticker])
            ble = fundamentals.get_balance(tickers[ticker])
            ico = fundamentals.get_income(tickers[ticker])
            csh = fundamentals.get_cash_flow(tickers[ticker])
            for val in [
                (ica, Tag.ICA),
                (ifc, Tag.ICF),
                (rec, Tag.REC),
                (ble, Tag.BLE),
                (ico, Tag.ICO),
                (csh, Tag.CSH),
            ]:
                # hash stock name, tag and data
                m = hashlib.sha256()
                m.update(val[1].encode('UTF-8'))
                m.update(stock.name.encode('UTF-8'))
                data_str = json.dumps(val[0])
                m.update(data_str.encode('UTF-8'))
                shahash = m.hexdigest()
                # only add data if not exist
                if Data.get(hash=shahash) is None:
                    tag = Tag.get(name=val[1])
                    obj = Data(
                        data=val[0],
                        hash=shahash,
                        data_item=DataItem(item=Item(tags=[tag])),
                    )
                    stock.data_items.add(obj.data_item)
        commit()
