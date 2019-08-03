#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import datetime
import logging
from datetime import timedelta

from pystockdb.db.schema.stocks import Symbol, Tag
from pystockdb.tools.base import DBBase


class CreateAndFillDataBase(DBBase):
    """
    Database installer
    """

    def __init__(self, arguments: dict, logger: logging.Logger):
        super(CreateAndFillDataBase, self).__init__(arguments, logger)
        self.logger = logger
        self.currency = arguments['currency']
        self.history = arguments['max_history']
        self.indices_list = arguments['indices']

    def build(self):
        """
        Starts the database installation
        :return:
        """
        # add indices and stocks to db
        if not self.indices_list:
            return 0
        self.add_indices_and_stocks(self.indices_list)
        # add historical data
        if self.currency not in [Tag.EUR, Tag.USD]:
            self.logger.warning(
                'Currency {} is not supported.'.format(self.currency)
            )
            return -1
        # stocks
        symbols = Symbol.select(lambda t: (Tag.YAO in t.item.tags.name and
                                self.currency in t.item.tags.name) or
                                Tag.IDX in t.item.tags.name)
        end = datetime.datetime.now()
        start = end - timedelta(days=self.history * 365)
        self.download_historicals(symbols, start=start.strftime('%Y-%m-%d'),
                                  end=end.strftime('%Y-%m-%d'))
        return 0
