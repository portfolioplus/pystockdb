#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from datetime import datetime
from pony.orm import Database, PrimaryKey, Set, Required, Optional, Json


db = Database()


class Index(db.Entity):
    uid = PrimaryKey(int, auto=True)
    stocks = Set('Stock')
    price_item = Required('PriceItem')
    name = Required(str)


class Stock(db.Entity):
    id = PrimaryKey(int, auto=True)
    indexs = Set(Index)
    name = Optional(str)
    orders = Set('Order')
    price_item = Required('PriceItem')
    data_items = Set('DataItem')


class Signal(db.Entity):
    id = PrimaryKey(int, auto=True)
    result = Optional('Result')
    orders = Set('Order')
    item = Required('Item')
    price_items = Set('PriceItem')
    data_item = Required('DataItem')


class Tag(db.Entity):
    YAO = 'yahoo'
    GOG = 'google'
    USD = 'USD'
    EUR = 'EUR'
    IDX = 'index'
    ICA = 'incomeanalysis'
    ICF = 'incomefacts'
    REC = 'recommendation'
    ICO = 'income'
    BLE = 'balance'
    CSH = 'cash'

    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    items = Set('Item')
    type = Required('Type')


class Type(db.Entity):
    IND = 'industry'
    REG = 'region'
    SYM = 'symbol'
    CUR = 'currency'
    MSC = 'misc'
    FDM = 'fundamentals'

    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    tags = Set(Tag)

    def add_tags(self, names):
        """Add multiple tags to item object

        Arguments:
            names {list} -- list of tag names
        """
        for name in names:
            self.tags.create(name=name)


class Result(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Required(datetime)
    value = Required(float)
    status = Required(int)
    signal = Required(Signal)
    arguments = Set('Argument')


class Symbol(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str, unique=True)
    price_item = Required('PriceItem')
    prices = Set('Price')
    item = Required('Item')


class Price(db.Entity):
    id = PrimaryKey(int, auto=True)
    open = Required(float)
    close = Required(float)
    high = Required(float)
    low = Required(float)
    volume = Required(int)
    date = Required(datetime)
    symbol = Required(Symbol)


class Portfolio(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    orders = Set('Order')
    cash = Required(float)
    value = Required(float)
    invest = Required(float)


class Order(db.Entity):
    id = PrimaryKey(int, auto=True)
    portfolio = Required(Portfolio)
    stock = Required(Stock)
    signals = Set(Signal)
    size = Optional(int)
    price = Optional(float)


class Item(db.Entity):
    id = PrimaryKey(int, auto=True)
    signal = Optional(Signal)
    tags = Set(Tag)
    price_item = Optional('PriceItem')
    argument = Optional('Argument')
    data_item = Optional('DataItem')
    symbol = Optional(Symbol)

    def add_tags(self, tags):
        """Add multiple tags to item object

        Arguments:
            tags {list} -- list of Tags
        """
        for tag in tags:
            self.tags.add(tag)


class PriceItem(db.Entity):
    id = PrimaryKey(int, auto=True)
    item = Required(Item)
    stock = Optional(Stock)
    index = Optional(Index)
    symbols = Set(Symbol)
    signals = Set(Signal)


class Argument(db.Entity):
    id = PrimaryKey(int, auto=True)
    arg = Optional(float)
    item = Required(Item)
    result = Required(Result)


class Data(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Required(datetime, default=datetime.now())
    data = Required(Json)
    hash = Required(str)
    data_item = Required('DataItem')


class DataItem(db.Entity):
    id = PrimaryKey(int, auto=True)
    item = Required(Item)
    datas = Set(Data)
    signal = Optional(Signal)
    stock = Optional(Stock)
