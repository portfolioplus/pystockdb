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

from pystockdb.db.schema.stocks import Price, Stock, Data
from pystockdb.tools.create import CreateAndFillDataBase
from pystockdb.tools.update import UpdateDataBaseStocks
from pystockdb.tools.sync import SyncDataBaseStocks


def create_database(db_name):
    logger = logging.getLogger('test')
    config = {
        'max_history': 1,
        'indices': ['DAX'],
        'currency': 'EUR',
        'db_args': {
            'provider': 'sqlite',
            'filename': db_name,
            'create_db': True
        },
    }
    create = CreateAndFillDataBase(config, logger)
    create.build()


class TestDatabase(unittest.TestCase):

    def tearDown(self):
        super(TestDatabase, self).tearDown()

    def test_create(self):
        """
        Test database client
        :return:
        """
        with freeze_time('2019-01-14'):
            create_database('database_create.sqlite')
        with db_session:
            stocks = Stock.select().count()
            self.assertEqual(stocks, 30)
            prices = list(select(max(p.date) for p in Price))
            self.assertEqual(len(prices), 1)
            self.assertEqual(prices[0].strftime('%Y-%m-%d'), '2019-01-14')

    def test_update(self):
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
        update.build()
        with db_session:
            price_ctx_now = Price.select().count()
            data_ctx_now = Data.select().count()
            self.assertEqual(price_ctx_now, price_ctx)
            self.assertEqual(data_ctx_now, data_ctx)

    def test_sync(self):
        """Tests sync tool
        """
        logger = logging.getLogger('test')
        config = {
            'max_history': 1,
            'indices': ['DAX', 'CAC 40'],
            'currency': 'EUR',
            'db_args': {
                'provider': 'sqlite',
                'filename': 'database_create.sqlite',
            },
        }
        sync = SyncDataBaseStocks(config, logger)
        sync.build()
        with db_session:
            stocks = Stock.select().count()
            self.assertEqual(stocks, 70)


if __name__ == "__main__":
    unittest.main()
