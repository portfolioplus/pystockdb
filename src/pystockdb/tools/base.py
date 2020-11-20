#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging

from pony.orm import commit, db_session, core
from pytickersymbols import PyTickerSymbols

from pystockdb.db.schema.stocks import (
    Index,
    Item,
    PriceItem,
    Stock,
    Symbol,
    Tag,
    Type,
    db,
)
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
        try:
            db.bind(**self.db_args)
        except core.BindingError:
            pass
        else:
            db.generate_mapping(check_tables=False)

        if self.arguments.get('create', False):
            db.drop_all_tables(with_all_data=True)
            db.create_tables()
            self.__insert_initial_data()

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
            if yah_sym is None:
                self.logger.warning(
                    'Can not translate {} into yahoo symbol'.format(index_name)
                )
                continue
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
                'Add stock {}:{} to index.'.format(
                    index.name, stock_in_db.name
                )
            )
            index.stocks.add(stock_in_db)
        else:
            self.logger.info(
                'Add stock {}:{} to db'.format(
                    index.name, stock_info[Type.SYM]
                )
            )
            # create stock
            stock = Stock(
                name=stock_info['name'], price_item=PriceItem(item=Item())
            )
            # add symbols
            yao = Tag.get(name=Tag.YAO)
            gog = Tag.get(name=Tag.GOG)
            usd = Tag.get(name=Tag.USD)
            eur = Tag.get(name=Tag.EUR)
            rub = Tag.get(name=Tag.RUB)
            for symbol in stock_info['symbols']:
                if Tag.GOG in symbol and symbol[Tag.GOG] != '-':
                    self.__create_symbol(
                        stock, Tag.GOG, gog, symbol, eur, usd, rub
                    )
                if Tag.YAO in symbol and symbol[Tag.YAO] != '-':
                    self.__create_symbol(
                        stock, Tag.YAO, yao, symbol, eur, usd, rub
                    )
            index.stocks.add(stock)
            # connect stock with industry and country
            # country
            name = stock_info['country']
            country = Tag.select(
                lambda t: t.name == name and t.type.name == Type.REG
            ).first()
            country.items.add(stock.price_item.item)
            # industry
            indus = stock_info['industries']
            industries = Tag.select(
                lambda t: t.name in indus and t.type.name == Type.IND
            )
            for industry in industries:
                industry.items.add(stock.price_item.item)

    @db_session
    def __create_symbol(
        self, stock, my_tag, my_tag_item, symbol, eur, usd, rub
    ):
        if my_tag in symbol and symbol[my_tag] != '-':
            cur = None
            if (
                symbol[my_tag].startswith('FRA:')
                or symbol[my_tag].endswith('.F')
                or symbol[my_tag].startswith('BME:')
                or symbol[my_tag].endswith('.MC')
            ):
                cur = eur
            elif (
                symbol[my_tag].startswith('NYSE:')
                or symbol[my_tag].startswith('OTCMKTS:')
                or symbol[my_tag].startswith('NASDAQ:')
                or ('.' not in symbol[my_tag] and ':' not in symbol[my_tag])
            ):
                cur = usd
            elif symbol[my_tag].startswith('MCX:') or symbol[my_tag].endswith(
                '.ME'
            ):
                cur = rub

            item = Item()
            if cur:
                item.add_tags([my_tag_item, cur])
            else:
                self.logger.warning(
                    'Currency detection for Symbol {} failed.'.format(
                        symbol[my_tag]
                    )
                )

            if Symbol.get(name=symbol[my_tag]):
                self.logger.warning(
                    'Symbol {} is related to more than one'
                    ' stock.'.format(symbol[my_tag])
                )
            else:
                stock.price_item.symbols.create(item=item, name=symbol[my_tag])

    @db_session
    def download_historicals(self, symbols, start, end):
        if not (start and end):
            return False
        crawler = DataCrawler()
        chunks = [symbols[x: x + 50] for x in range(0, len(symbols), 50)]
        for chunk in chunks:
            ids = [symbol.name for symbol in chunk]
            if ids is None:
                continue
            print(ids)
            series = crawler.get_series_stack(ids, start=start, end=end)
            for symbol in chunk:
                self.logger.debug(
                    'Add prices for {} from {} until {}.'.format(
                        symbol.name, start, end
                    )
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
        Type(name=Type.CUR).add_tags([Tag.USD, Tag.EUR, Tag.RUB])
        Type(name=Type.FDM).add_tags(
            [Tag.ICA, Tag.ICF, Tag.REC, Tag.ICO, Tag.BLE, Tag.CSH]
        )
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
