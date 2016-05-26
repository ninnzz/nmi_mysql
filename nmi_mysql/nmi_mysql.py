"""
    Custom mysql wrapper for sqlalchemy
    Useful for raw queries and scripting
"""

from sqlalchemy import create_engine, text
from pymysql.converters import escape_item, escape_string

import re
import logging


CONFIG_KEYS = ['host', 'user', 'password', 'db', 'port']
MAX_POOL_SIZE = 10


class DB(object):

    def __init__(self, conf):
        for c in CONFIG_KEYS:
            if c not in conf:
                raise ValueError('Invalid config object')

        self.logger = logging.getLogger('database')
        self.charset = 'utf8mb4'
        self.con = None

        self.engine = create_engine(
            self._sql_alchemy_format(conf),
            pool_size=conf.get('max_pool_size', MAX_POOL_SIZE)
        )

    def _sql_alchemy_format(self, conf):
        return ''.join([
            'mysql+pymysql://',
            conf['user'] + ':',
            conf['password'] + '@',
            conf['host'] + ':',
            str(conf['port']) + '/',
            conf['db'],
            '?charset=' + self.charset
        ])

    def _generate_query(self, _query, _params):
        query = re.sub('\?', '%s', _query)

        if not isinstance(_params, list):
            return query % self._to_string(_params)

        params = []
        values = []
        for param in _params:
            if isinstance(param, tuple):
                values.append('(' + self._to_string(param) + ')')

            else:
                params.append(self._to_string(param))

        if values:
            params = ', '.join(values)
            query = query % params[1:-1]

        else:
            query = query % tuple(params)

        return query

    def _to_string(self, temp):
        if isinstance(temp, (list, tuple)):
            tmp = []
            for item in temp:
                tmp.append(self._to_string(item))

            return ', '.join(tmp)

        elif isinstance(temp, dict):
            tmp = []
            for key in temp:
                tmp.append(key + ' = ' + self._to_string(temp[key]))

            return ', '.join(tmp)

        elif isinstance(temp, str):
            return escape_string(temp.replace('%', '%%'))

        else:
            return escape_item(temp, self.charset)

    def connect(self):
        self.con = self.engine.connect()

    def close(self):
        self.con.close()

    def query(self, _query, _params=None):
        if not self.con:
            self.connect()

        result = None
        query = _query

        if _params:
            query = self._generate_query(_query, _params)

        try:
            result = self.con.execute(text(query))

            if query.lower().strip().find('select') == 0:
                return [dict(row) or row for row in result]

            else:
                return {
                    'affected_rows': result.rowcount
                }

        except Exception as err:
            self.logger.warn(err)
            raise err

        return result
