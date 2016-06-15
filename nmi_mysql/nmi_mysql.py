"""
    Custom mysql wrapper for sqlalchemy
    Useful for raw queries and scripting
"""

from sqlalchemy import create_engine
from pymysql.cursors import DictCursor

import re
import logging


CONFIG_KEYS = ['host', 'user', 'password', 'db', 'port']
MAX_POOL_SIZE = 10


class DB(object):

    def __init__(self, conf, autoconnect=False):
        for c in CONFIG_KEYS:
            if c not in conf:
                raise ValueError('Invalid config object')

        self.logger = logging.getLogger('database')
        self.charset = 'utf8mb4'
        self.con = None
        self._last_query = None
        self._last_params = None

        self.engine = create_engine(
            self._sql_alchemy_format(conf),
            pool_size=conf.get('max_pool_size', MAX_POOL_SIZE)
        )

        if autoconnect:
            self.connect()

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

    def _generate_query(self, _query, _params, _executemany):
        query = re.sub('\?', '%s', _query)

        if not isinstance(_params, list):
            return (query % self._to_string(_params), _params)

        params = []
        other_queries = []

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

            other_queries.append(self._to_string(param))

        if _executemany or (len(params) and isinstance(params[0], tuple)):
            # Add %s based on the number of columns to fill in insertion
            return (query % ('%s,' * len(params[0]))[:-1], params, True)

        else:
            return (query % tuple(other_queries), params, False)

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

    def _get_results(self, _cursor):
        if _cursor._rows is None:
            return {
                'affected_rows': _cursor.rowcount
            }

        result = _cursor.fetchall()

        return result if result else []

    def connect(self, retry=0):
        try:
            self.con = self.engine.connect()

        except Exception as err:
            if not retry:
                raise err

            tries = 0
            while True:
                self.logger.info('Retrying to connect to database')
                try:
                    self.con = self.engine.connect()
                    break

                except Exception as err2:
                    tries += 1
                    if tries == retry:
                        self.logger.error('Failed to connect to database')
                        raise err2

    def close(self):
        self.con.close()

    def query(self, query, params=None, executemany=False):
        if not self.con:
            self.connect()

        if not params:
            params = []

        (_query, _params, _executemany) = self._generate_query(query, params,
                                                               executemany)

        results = []
        self._last_query = _query
        self._last_params = _params

        try:
            cursor = self.con.connection.cursor(DictCursor)

            if _executemany:
                cursor.executemany(_query, _params)

            else:
                cursor.execute(_query, _params)

            results.append(self._get_results(cursor))

            while cursor.nextset():
                results.append(self._get_results(cursor))

        except Exception as err:
            self.logger.warn(err)
            raise err

        return results if len(results) > 1 else results[0]
