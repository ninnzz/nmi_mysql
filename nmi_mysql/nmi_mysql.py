"""
    Custom mysql wrapper for sqlalchemy
    Useful for raw queries and scripting
"""

import re
import inspect
import logging
import warnings

from functools import wraps

from pymysql.cursors import DictCursor

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

CONFIG_KEYS = ['host', 'user', 'password', 'db', 'port']
MAX_POOL_SIZE = 10


# NOTE(kgriffs): We don't want our deprecations to be ignored by default,
# so create our own type.
class DeprecatedWarning(UserWarning):
    pass


# https://gist.githubusercontent.com/kgriffs/8202106/raw/e2f7b64d732e598679ae12954a993f7384130158/util.py
def deprecated(instructions):
    """ Flags a method as deprecated.
        Args:
            instructions: A human-friendly string of instructions, such
                as: 'Please migrate to add_proxy() ASAP.'
    """

    def decorator(func):
        """ This is a decorator which can be used to mark functions
            as deprecated. It will result in a warning being emitted
            when the function is used.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            message = 'Call to deprecated function {}. {}'.format(
                func.__name__,
                instructions
            )

            frame = inspect.currentframe().f_back

            warnings.warn_explicit(
                message,
                category=DeprecatedWarning,
                filename=inspect.getfile(frame.f_code),
                lineno=frame.f_lineno
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


class DB(object):
    def __init__(self, conf, *args, **kwargs):
        for c in CONFIG_KEYS:
            if c not in conf:
                raise ValueError('Invalid config object')

        self.logger = logging.getLogger('database')
        self.charset = 'utf8mb4'
        self._last_query = None
        self._last_params = None

        self.engine = create_engine(
            self._sql_alchemy_format(conf),
            pool_size=conf.get('max_pool_size', MAX_POOL_SIZE)
        )

    @deprecated('DB.query() closes the connection. No need to call this.')
    def close(self, *args, **kwargs):
        pass

    @deprecated('DB.query() connects to database. No need to call this.')
    def connect(self, *args, **kwargs):
        pass

    def _sql_alchemy_format(self, _conf):
        return ''.join([
            'mysql+pymysql://',
            _conf['user'] + ':',
            _conf['password'] + '@',
            _conf['host'] + ':',
            str(_conf['port']) + '/',
            _conf['db'],
            '?charset=' + self.charset
        ])

    def _connect(self, _retry_connection=0):
        try:
            return self.engine.connect()

        except Exception as err:
            if not _retry_connection:
                raise err

            tries = 0

            while True:
                self.logger.info('Retrying to connect to database..')

                try:
                    return self.engine.connect()

                except Exception as err2:
                    tries += 1

                    if tries == _retry_connection:
                        self.logger.error('Failed to connect to database.')

                        raise err2

    def _generate_query(self, _query, _params):
        query = re.sub('%s', '{}', re.sub('\?', '{}', _query))
        query = re.sub('%', '%%', query)

        if not isinstance(_params, list):
            return query.format(self._to_string(_params)), _params

        params = []
        query_params = []

        # Flatten out _params to a list
        for param in _params:
            if isinstance(param, list):
                # Append the contents of list param to the list params
                params.extend(param)

            elif isinstance(param, dict):
                # Append the values of dict param to the list params
                for key in param:
                    params.append(param[key])

            else:
                # Append param for types other than list or dict
                params.append(param)

            query_params.append(self._to_string(param))

        if len(params) and isinstance(params[0], tuple):
            # Add %s based on the number of columns to fill in insertion
            return query.format(('%s,' * len(params[0]))[:-1]), params

        return query.format(*tuple(query_params)), params

    def _to_string(self, _temp):
        # Add %s for each item in the list
        if isinstance(_temp, list):
            tmp = []

            for item in _temp:
                tmp.append(self._to_string(item))

            return ', '.join(tmp)

        # Add <column> = %s for each item in the dict
        elif isinstance(_temp, dict):
            tmp = []

            for key in _temp:
                tmp.append(key + ' = ' + self._to_string(_temp[key]))

            return ', '.join(tmp)

        return '%s'

    def _execute(self, _query, _params, _multi=False, _retry_connection=0):

        def get_multi_results(_cursor):
            if _cursor._rows is None:
                return {
                    'affected_rows': _cursor.rowcount
                }

            _result = _cursor.fetchall()

            return _result if _result else []

        con = self._connect(_retry_connection)

        if not _params:
            _params = []

        self._last_query = _query
        self._last_params = _params

        query, params = self._generate_query(_query, _params)

        try:
            if _multi:
                result = []
                cursor = con.connection.cursor(DictCursor)

                cursor.execute(query, params)

                result.append(get_multi_results(cursor))

                while cursor.nextset():
                    result.append(get_multi_results(cursor))

            else:
                result = con.execute(query, *params)

                if result.returns_rows:
                    result = [dict(row) for row in result]

                else:
                    result = {
                        'affected_rows': result.rowcount
                    }

            con.close()

        except SQLAlchemyError as err:
            self.logger.warn(err.orig)

            raise err.orig

        except Exception as err:
            self.logger.warn(err)

            raise err

        return result

    def multi_query(self, query, params=None, retry_connection=0):
        return self._execute(query, params, True, retry_connection)

    def query(self, query, params=None, retry_connection=0):
        return self._execute(query, params, False, retry_connection)
