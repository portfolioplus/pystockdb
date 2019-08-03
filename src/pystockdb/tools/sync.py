#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import logging

from pony.orm import db_session, select

from pystockdb.db.schema.stocks import Index
from pystockdb.tools.create import CreateAndFillDataBase


class SyncDataBaseStocks(CreateAndFillDataBase):
    """
    Sync Tool for autotrader database
    """

    def __init__(self, arguments: dict, logger: logging.Logger):
        # create db is not allowed during sync
        if 'db_args' in arguments and 'create_db' in arguments['db_args']:
            arguments['db_args']['create_db'] = False
        super(SyncDataBaseStocks, self).__init__(arguments, logger)

    def build(self):
        """
        Starts the update process
        :return: nothing
        """
        self.__set_indices()
        super(SyncDataBaseStocks, self).build()

    @db_session
    def __set_indices(self):
        indices_db = list(select(ind.name for ind in Index))
        self.indices_list = [ind for ind in self.indices_list
                             if ind not in indices_db]
