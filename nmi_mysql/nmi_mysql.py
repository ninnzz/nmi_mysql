"""
    Custom mysql wrapper for pymysql
    Usefull for raw queries and scripting
"""

import re
import logging
import pymysql.cursors
from queue import Queue


CONFIG_KEYS = ['host', 'user', 'password', 'db', 'port']


class DB(object):

    def __init__(self, conf, max_pool_size=10):
        for c in CONFIG_KEYS:
            if c not in conf:
                raise ValueError('Invalid config object')

        self.conf = conf
        self.max_pool_size = max_pool_size
        self._initialize_pool()

    def _initialize_pool(self):
        self.pool = Queue(maxsize=self.max_pool_size)

        for _ in range(0, self.max_pool_size):
            self.pool.put_nowait(Connection(self.conf))

    def connect(self):
        con = self.pool.get()
        con.connect()

        return con

    def close(self, con):
        if isinstance(con, Connection):
            con.close()
            self.pool.put(con)


class Connection(object):

    def __init__(self, conf):
        self.logger = logging.getLogger('database')
        self.host = conf['host']
        self.user = conf['user']
        self.password = conf['password']
        self.db_conn = conf['db']
        self.port = int(conf['port'])
        self.handle = None
        self.connected = False

    def __del__(self):
        self.close()

    def connect(self):
        self.logger.info('Trying to connect to mysql database')

        try:
            con = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db_conn,
                port=self.port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )

        except Exception as err:
            self.logger.error('Failed to connect to db')
            self.logger.warn('Error:')
            self.logger.info(err)

            raise err

        self.logger.info('Connection to mysql')
        self.connected = True
        self.handle = con

        return True

    def close(self):
        try:
            if self.connected:
                self.handle.close()
                self.connected = False
                self.handle = None

        except Exception as err:
            self.logger.warn('Failed to close connection')
            self.logger.warn(err)

            raise err

        return None

    def query(self, _query, _params=None):
        """
            self.handle holds the connection
            _query is the query
            _params holds the variables need by the query
        """

        result = None
        query = _query

        if _params:
            query = self.generate_query(_query, _params)

        try:
            with self.handle.cursor() as cursor:
                cursor.execute(query, ())

                if query.lower().strip().find('select') == 0:
                    result = list(cursor.fetchall())

                else:
                    result = {
                        'affected_rows': cursor.rowcount
                    }

        except Exception as err:
            self.logger.warn(err)
            raise err

        self.handle.commit()

        return result

    def generate_query(self, _query, _params):
        query = re.sub('\?', '%s', _query)

        if not isinstance(_params, list):
            return query % self.to_string(_params)

        params = []
        values = []
        for param in _params:
            if isinstance(param, tuple):
                values.append('(' + self.to_string(param) + ')')

            else:
                params.append(self.to_string(param))

        if values:
            params = ', '.join(values)
            query = query % params[1:-1]

        else:
            query = query % tuple(params)

        return query

    def to_string(self, temp):
        if isinstance(temp, (list, tuple)):
            tmp = []
            for item in temp:
                if isinstance(item, str):
                    item = item.replace('%', '%%')
                tmp.append(self.handle.escape(item))

            return ', '.join(tmp)

        elif isinstance(temp, dict):
            tmp = []
            for key in temp:
                if isinstance(temp[key], str):
                    temp[key] = temp[key].replace('%', '%%')
                tmp.append(key + ' = ' + self.handle.escape(temp[key]))

            return ', '.join(tmp)

        elif isinstance(temp, str):
            return self.handle.escape(temp.replace('%', '%%'))

        else:
            return self.handle.escape(temp)
