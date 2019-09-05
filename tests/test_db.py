#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import datetime
import logging
import unittest

from freezegun import freeze_time
from pony.orm import db_session, select

from pystockdb.db.schema.stocks import Data, Index, Price, Stock, Symbol
from pystockdb.tools.base import DBBase
from pystockdb.tools.create import CreateAndFillDataBase
from pystockdb.tools.sync import SyncDataBaseStocks
from pystockdb.tools.update import UpdateDataBaseStocks


class TestDatabase(unittest.TestCase):

    def tearDown(self):
        super(TestDatabase, self).tearDown()

    def test_1_create(self):
        """
        Test database client
        :return:
        """
        config = {
            'max_history': 1,
            'indices': [],
            'currencies': ['EUR'],
            'db_args': {
                'provider': 'sqlite',
                'filename': 'database_create.sqlite',
                'create_db': True
            },
        }
        logger = logging.getLogger('test')
        create = CreateAndFillDataBase(config, logger)
        self.assertEqual(create.build(), 0)
        config['indices'] = ['DAX']
        config['currencies'] = ['RUB']
        create = CreateAndFillDataBase(config, logger)
        self.assertEqual(create.build(), -1)
        config['currencies'] = ['EUR', 'USD']
        # check setup with multiple currencies
        with freeze_time('2019-01-14'):
            create = CreateAndFillDataBase(config, logger)
            self.assertEqual(create.build(), 0)
        with db_session:
            # check euro
            prices_ctx = Price.select(
                lambda p: p.symbol.name == 'IFX.F'
            ).count()
            self.assertGreater(prices_ctx, 1)
            # check usd
            prices_ctx = Price.select(
                lambda p: p.symbol.name == 'IFNNF'
            ).count()
            self.assertGreater(prices_ctx, 1)
        with freeze_time('2019-01-14'):
            config['currencies'] = ['EUR']
            create = CreateAndFillDataBase(config, logger)
            self.assertEqual(create.build(), 0)
        with db_session:
            stocks = Stock.select().count()
            self.assertEqual(stocks, 30)
            prices = list(select(max(p.date) for p in Price))
            self.assertEqual(len(prices), 1)
            self.assertEqual(prices[0].strftime('%Y-%m-%d'), '2019-01-14')

    @db_session
    def test_2_dbbase(self):
        config = {
            'db_args': {
                'provider': 'sqlite',
                'filename': 'database_create.sqlite',
                'create_db': False
            }
        }
        logger = logging.getLogger('test')
        dbbase = DBBase(config, logger)
        ind = Index.get(name='test123')
        if ind:
            ind.delete()
        sym = Symbol.get(name='test123')
        if sym:
            sym.delete()
        self.assertRaises(NotImplementedError, dbbase.build)
        self.assertFalse(dbbase.download_historicals(None, None, None))

        # override pytickersymbols
        def get_stocks_by_index(name):
            stock = {
                'name': 'adidas AG',
                'symbol': 'ADS',
                'country': 'Germany',
                'indices': ['DAX', 'test123'],
                'industries': [],
                'symbols': []
            }
            return [stock]

        def index_to_yahoo_symbol(name):
            return 'test123'

        dbbase.ticker_symbols.get_stocks_by_index = get_stocks_by_index
        dbbase.ticker_symbols.index_to_yahoo_symbol = index_to_yahoo_symbol
        dbbase.add_indices_and_stocks(['test123'])
        ads = Stock.select(
            lambda s: 'test123' in s.indexs.name
        ).first()
        self.assertNotEqual(ads, None)
        Index.get(name='test123').delete()
        Symbol.get(name='test123').delete()

    def test_3_update(self):
        """
        Test database client update
        :return:
        """
        logger = logging.getLogger('test')
        config = {
            'symbols': ['ALL'],
            'prices': True,
            'fundamentals': True,
            'db_args': {
                'provider': 'sqlite',
                'filename': 'database_create.sqlite',
                'create_db': False
            },
        }
        update = UpdateDataBaseStocks(config, logger)
        update.build()
        with db_session:
            prices = list(select(max(p.date) for p in Price))
            self.assertEqual(len(prices), 1)
            my_date = datetime.datetime.strptime('2019-01-14',
                                                 '%Y-%m-%d')
            self.assertGreater(prices[0], my_date)
            price_ctx = Price.select().count()
            data_ctx = Data.select().count()
            self.assertGreater(data_ctx, 1)
            self.assertGreater(price_ctx, 1)
        update.build()
        with db_session:
            price_ctx_now = Price.select().count()
            data_ctx_now = Data.select().count()
            self.assertGreaterEqual(price_ctx_now, price_ctx)
            self.assertGreaterEqual(data_ctx_now, data_ctx)
        config['symbols'] = ['ADS.F']
        update = UpdateDataBaseStocks(config, logger)
        update.build()

    def test_4_sync(self):
        """Tests sync tool
        """
        logger = logging.getLogger('test')
        config = {
            'max_history': 1,
            'indices': ['DAX', 'CAC 40'],
            'currencies': ['EUR'],
            'db_args': {
                'provider': 'sqlite',
                'filename': 'database_create.sqlite',
                'create_db': True  # should set to false
            },
        }
        sync = SyncDataBaseStocks(config, logger)
        sync.build()
        with db_session:
            stocks = Stock.select().count()
            self.assertEqual(stocks, 70)

    @db_session
    def test_5_query_data(self):
        ifx = Stock.select(
            lambda s: 'IFX.F' in s.price_item.symbols.name
        ).first()
        dataNone = ifx.get_data_attr('incomNone', 'netIncome')
        self.assertIsNone(dataNone)
        data = ifx.get_data_attr('income', 'netIncome')
        self.assertIsInstance(data, float)
        data2 = ifx.get_data_attr('income', 'netIncome', quarter_diff=4)
        self.assertIsInstance(data2, float)
        data3 = ifx.get_data_attr('income', 'netIncome', quarter_diff=1)
        self.assertIsInstance(data3, float)
        data4 = ifx.get_data_attr('income', 'netIncome', annual=True)
        self.assertIsInstance(data4, float)
        rat = ifx.get_data_attr('recommendation', 'rating')
        mea = ifx.get_data_attr('recommendation', 'measures')
        eps = ifx.get_data_attr('recommendation', 'eps')
        self.assertEqual(mea, -1)
        self.assertIsInstance(rat, float)
        self.assertIsInstance(eps, float)

    def test_6_create_flat(self):
        """
        Test flat create
        :return:
        """
        config = {
            'max_history': 1,
            'indices': ['DAX'],
            'currencies': ['EUR'],
            'prices': False,  # disables price downloading
            'db_args': {
                'provider': 'sqlite',
                'filename': 'database_create.sqlite',
                'create_db': True
            },
        }
        logger = logging.getLogger('test')
        create = CreateAndFillDataBase(config, logger)
        self.assertEqual(create.build(), 0)
        with db_session:
            # check euro
            prices_ctx = select(p for p in Price).count()
            self.assertEqual(prices_ctx, 0)

        config = {
            'symbols': ['IFX.F', 'ADS.F'],
            'prices': True,
            'fundamentals': True,
            'max_history': 1,
            'db_args': {
                'provider': 'sqlite',
                'filename': 'database_create.sqlite',
                'create_db': False
            },
        }
        update = UpdateDataBaseStocks(config, logger)
        self.assertEqual(update.build(), 0)
        with db_session:
            prices_ctx = Price.select(
                lambda p: p.symbol.name == 'IFX.F'
            ).count()
            self.assertGreater(prices_ctx, 1)
            prices_ctx = Price.select(
                lambda p: p.symbol.name == 'ADS.F'
            ).count()
            self.assertGreater(prices_ctx, 1)
            data_ctx = select(d for d in Data).count()
            self.assertEqual(data_ctx, 12)

if __name__ == "__main__":
    unittest.main()
