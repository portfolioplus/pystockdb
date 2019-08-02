[![Codacy Badge](https://api.codacy.com/project/badge/Grade/addbee49fdaa4b40aa162f32d7cd3478)](https://app.codacy.com/app/SlashGordon/pystockdb?utm_source=github.com&utm_medium=referral&utm_content=portfolioplus/pystockdb&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.org/portfolioplus/pystockdb.svg?branch=master)](https://travis-ci.org/portfolioplus/pystockdb)
[![Coverage Status](https://coveralls.io/repos/github/portfolioplus/pystockdb/badge.svg?branch=master)](https://coveralls.io/github/portfolioplus/pystockdb?branch=master)

# pystockdb

database for stocks based on pony.orm:

# quick start

Install sqlite stock db:

```python
import logging
from pystockdb.tools.create import CreateAndFillDataBase

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
```
# issue tracker

[https://github.com/portfolioplus/pystockdb/issuese](https://github.com/portfolioplus/pystockdb/issues")
