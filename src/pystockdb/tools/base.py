#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging

from pony.orm import commit, db_session

from pytickersymbols import PyTickerSymbols

from pystockdb.db.schema.stocks import (Index, Item, PriceItem, Stock, Tag,
                                        Type, db)
from pystockdb.tools.data_crawler import DataCrawler


class DBBase:
    """
    Database installer
    """

    def __init__(self, arguments: dict, logger: logging.Logger):
        self.logger = logger
        self.db_args = arguments["db_args"]
        self.arguments = arguments
        self.ticker_symbols = PyTickerSymbols()
        # has connection
        if db.provider is None:
            # prepare db
            db.bind(**self.db_args)
            if self.db_args.get('create_db', False):
                db.generate_mapping(check_tables=False)
                db.drop_all_tables(with_all_data=True)
                db.create_tables()
                self.__insert_initial_data()
            else:
                db.generate_mapping()

    def build(self):
        """
        Starts the database installation
        :return:
        """
        raise NotImplementedError

    @db_session
    def add_indices_and_stocks(self, indices_list):
        for index_name in indices_list:
            index = Index(name=index_name, price_item=PriceItem(item=Item()))
            # add index symbol
            yah_sym = self.ticker_symbols.index_to_yahoo_symbol(index_name)
            idx_item = Item()
            idx_item.tags.add(Tag.get(name=Tag.IDX))
            index.price_item.symbols.create(name=yah_sym, item=idx_item)
            stocks = self.ticker_symbols.get_stocks_by_index(index.name)
            for stock_info in stocks:
                self.__add_stock_to_index(index, stock_info)
            commit()

    def __add_stock_to_index(self, index, stock_info):
        stock_in_db = Stock.get(name=stock_info['name'])
        if stock_in_db:
            self.logger.info(
                'Add stock {}:{} to index.'.format(index.name,
                                                   stock_in_db.name)
            )
            index.stocks.add(stock_in_db)
        else:
            self.logger.info(
                'Add stock {}:{} to db'.format(index.name,
                                               stock_info[Type.SYM])
            )
            # create stock
            stock = Stock(name=stock_info['name'],
                          price_item=PriceItem(item=Item()))
            # add symbols
            yao = Tag.get(name=Tag.YAO)
            gog = Tag.get(name=Tag.GOG)
            usd = Tag.get(name=Tag.USD)
            eur = Tag.get(name=Tag.EUR)
            for symbol in stock_info['symbols']:
                if Tag.GOG in symbol:
                    cur = eur if symbol[Tag.GOG].startswith('FRA') else usd
                    item = Item()
                    item.add_tags([gog, cur])
                    stock.price_item.symbols.create(item=item,
                                                    name=symbol[Tag.GOG])
                if Tag.YAO in symbol:
                    cur = eur if symbol[Tag.YAO].endswith('.F') else usd
                    item = Item()
                    item.add_tags([yao, cur])
                    stock.price_item.symbols.create(item=item,
                                                    name=symbol[Tag.YAO])
            index.stocks.add(stock)
            # connect stock with industry and country
            # country
            name = stock_info['country']
            country = Tag.select(lambda t: t.name == name and
                                 t.type.name == Type.REG).first()
            country.items.add(stock.price_item.item)
            # industry
            indus = stock_info['industries']
            industries = Tag.select(lambda t: t.name in indus and
                                    t.type.name == Type.IND)
            for industry in industries:
                industry.items.add(stock.price_item.item)

    @db_session
    def download_historicals(self, symbols, start, end):
        if not (start and end):
            return False
        crawler = DataCrawler()
        chunks = [symbols[x:x + 50] for x in range(0, len(symbols), 50)]
        for chunk in chunks:
            ids = [symbol.name for symbol in chunk]
            series = crawler.get_series_stack(ids, start=start, end=end)
            for symbol in chunk:
                self.logger.debug(
                    'Add prices for {} from {} until {}.'.format(symbol.name,
                                                                 start, end)
                )
                for value in series[symbol.name]:
                    symbol.prices.create(**value)
            commit()
        return True

    @db_session
    def __insert_initial_data(self):
        # insert types
        region_type = Type(name=Type.REG)
        industry_type = Type(name=Type.IND)
        Type(name=Type.MSC).add_tags([Tag.IDX])
        Type(name=Type.SYM).add_tags([Tag.YAO, Tag.GOG])
        Type(name=Type.CUR).add_tags([Tag.USD, Tag.EUR])
        Type(name=Type.FDM).add_tags([Tag.ICA, Tag.ICF, Tag.REC,
                                      Tag.ICO, Tag.BLE, Tag.CSH])
        Type(name=Type.FIL)
        Type(name=Type.ICR)
        Type(name=Type.ARG)
        countries = self.ticker_symbols.get_all_countries()
        for country in countries:
            region_type.tags.create(name=country)
        industries = self.ticker_symbols.get_all_industries()
        for industry in industries:
            industry_type.tags.create(name=industry)
        commit()
