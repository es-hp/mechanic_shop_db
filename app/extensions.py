from flask_marshmallow import Marshmallow
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

ma = Marshmallow()

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

limiter = Limiter(key_func=get_remote_address)