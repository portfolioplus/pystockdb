import datetime
import logging
import pytest
from freezegun import freeze_time
from pony.orm import db_session, select
from pystockdb.db.schema.stocks import Data, Index, Price, Stock, Symbol, Tag
from pystockdb.tools.base import DBBase
from pystockdb.tools.create import CreateAndFillDataBase
from pystockdb.tools.sync import SyncDataBaseStocks
from pystockdb.tools.update import UpdateDataBaseStocks
from pystockdb.tools import ALL_SYMBOLS


def teardown():
    pass

@pytest.mark.order(3)
def test_create():
    """
    Test database client
    """
    config = {
        'max_history': 1,
        'indices': [],
        'currencies': ['EUR'],
        'create': True,
        'db_args': {
            'provider': 'sqlite',
            'filename': 'database_create.sqlite',
            'create_db': True
        },
    }
    logger = logging.getLogger('test')
    create = CreateAndFillDataBase(config, logger)
    assert create.build() == 0
    config['indices'] = ['DAX']
    config['currencies'] = ['CAD']
    create = CreateAndFillDataBase(config, logger)
    assert create.build() == -1
    config['currencies'] = ['EUR', 'USD']
    with freeze_time('2019-01-14'):
        create = CreateAndFillDataBase(config, logger)
        assert create.build() == 0
    with db_session:
        prices_ctx = Price.select(lambda p: p.symbol.name == 'IFX.F').count()
        assert prices_ctx > 1
        prices_ctx = Price.select(lambda p: p.symbol.name == 'IFNNF').count()
        assert prices_ctx > 1
    with freeze_time('2019-01-14'):
        config['currencies'] = ['EUR']
        create = CreateAndFillDataBase(config, logger)
        assert create.build() == 0
    with db_session:
        stocks = Stock.select().count()
        assert stocks == 40
        prices = list(select(max(p.date) for p in Price))
        assert len(prices) == 1
        assert prices[0].strftime('%Y-%m-%d') == '2019-01-11'

@pytest.mark.order(4)
def test_update():
    """
    Test database client update
    """
    logger = logging.getLogger('test')
    config = {
        'symbols': [ALL_SYMBOLS],
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
        assert len(prices) == 1
        my_date = datetime.datetime.strptime('2019-01-14', '%Y-%m-%d')
        assert prices[0] > my_date
        price_ctx = Price.select().count()
        data_ctx = Data.select().count()
        assert data_ctx > 1
        assert price_ctx > 1
    update.build()
    with db_session:
        price_ctx_now = Price.select().count()
        data_ctx_now = Data.select().count()
        assert price_ctx_now >= price_ctx
        assert data_ctx_now >= data_ctx
    config['symbols'] = ['ADS.F']
    update = UpdateDataBaseStocks(config, logger)
    update.build()

@pytest.mark.order(5)
def test_sync():
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
        assert stocks == 80

@pytest.mark.order(6)
@db_session
def test_query_data():
    ifx = Stock.select(lambda s: 'IFX.F' in s.price_item.symbols.name).first()
    dataNone = ifx.get_data('incomNone')
    assert dataNone is None
    data = ifx.get_data(Tag.ICO)
    assert isinstance(data, dict)
    data_info = ifx.get_data(Tag.INF)
    assert isinstance(data_info, dict)
    data_ble = ifx.get_data(Tag.BLE)
    assert isinstance(data_ble, dict)
    data_div = ifx.get_data(Tag.DIV)
    assert isinstance(data_div, dict)
    data_csh = ifx.get_data(Tag.CSH)
    assert isinstance(data_csh, dict)


@pytest.mark.order(7)
def test_create_flat():
    """
    Test flat create
    """
    config = {
        'max_history': 1,
        'indices': ['DAX'],
        'currencies': ['EUR'],
        'prices': False,  # disables price downloading
        'create': True,
        'db_args': {
            'provider': 'sqlite',
            'filename': 'database_create.sqlite',
            'create_db': True
        },
    }
    logger = logging.getLogger('test')
    create = CreateAndFillDataBase(config, logger)
    assert create.build() == 0
    with db_session:
        prices_ctx = select(p for p in Price).count()
        assert prices_ctx == 0

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
    assert update.build() == 0
    with db_session:
        prices_ctx = Price.select(lambda p: p.symbol.name == 'IFX.F').count()
        assert prices_ctx > 1
        prices_ctx = Price.select(lambda p: p.symbol.name == 'ADS.F').count()
        assert prices_ctx > 1
        data_ctx = select(d for d in Data).count()
        assert data_ctx > 1

@pytest.mark.order(8)
@db_session
def test_dbbase():
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
    with pytest.raises(NotImplementedError):
        dbbase.build()
    assert not dbbase.download_historicals(None, None, None)

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
    ads = Stock.select(lambda s: 'test123' in s.indexs.name).first()
    assert ads is not None
    Index.get(name='test123').delete()
    Symbol.get(name='test123').delete()