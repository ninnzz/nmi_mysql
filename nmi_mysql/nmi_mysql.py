"""
    Custom mysql wrapper for pymysql
    Usefull for raw queries and scripting
"""

import re
import logging
import pymysql.cursors

from multiprocessing import Queue


class DB():

    def __init__(self, conf, autoconnect=False):
        self.host = conf['host']
        self.user = conf['user']
        self.password = conf['password']
        self.db_conn = conf['db']
        self.port = int(conf['port'])
        self.handle = None
        self.connected = False
        self.logger = logging.getLogger('database')

        if autoconnect:
            self.connect()

    def __del__(self):
        self.close()

    def connect(self):

        self.logger.info('Trying to connect to mysql database')
        try:
            con = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                  db=self.db_conn, port=self.port, charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)

        except Exception as err:
            self.logger.error('Failed to connect to db')
            self.logger.warn('Error:')
            self.logger.info(err)
            return None

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
                self.logger.warn('Disconnecting to db, closing connection')

        except Exception as err:
            self.logger.warn('Failed to close connection')
            self.logger.warn(err)

        return None

    def query(self, _query, _params):
        """
            self.handle holds the connection
            _query is the query
            _params holds the variables need by the query
        """

        query = re.sub("\?", "%s", _query)
        result = None

        if isinstance(_params, list):
            params = []
            values = []
            for param in _params:
                if isinstance(param, tuple):
                    values.append('(' + self.to_string(param) + ')')

                else:
                    params.append(self.to_string(param))

            if values:
                params = ','.join(values)
                query = query % params[1:-1]

            else:
                query = query % tuple(params)

        else:
            query = query % self.to_string(_params)

        try:
            with self.handle.cursor() as cursor:
                cursor.execute(query, ())
                result = cursor.fetchall()
        except Exception as err:
            self.logger.warn(err)
            return None

        self.handle.commit()

        return result

    def execute_many(self, _query, _params):
        try:
            with self.handle.cursor() as cursor:
                cursor.executemany(_query, _params)
        except Exception as err:
            self.logger.warn(err)
            return None

        self.handle.commit()

    def to_string(self, temp):
        if isinstance(temp, (list, tuple)):
            tmp = ''
            for item in temp:
                tmp += ','
                if isinstance(item, str):
                    item = item.replace('%', '%%')
                tmp += self.handle.escape(item)

            return tmp[1:]

        elif isinstance(temp, str):
            return self.handle.escape(temp.replace('%', '%%'))

        else:
            return self.handle.escape(temp)


class ConnectionPool():

    def __init__(self, conf, max_pool_size=20):
        self.conf = conf
        self.max_pool_size = max_pool_size
        self.initialize_pool()

    def get_initialized_connection_pool(self):
        return self.pool

    def initialize_pool(self):
        self.pool = Queue(maxsize=self.max_pool_size)
        for _ in range(0, self.max_pool_size):
            self.pool.put_nowait(DB(self.conf, True))

    def get_connection(self):
        # returns a db instance when one is available
        db = self.pool.get(True)
        if not self.ping(db):
            db.connect()

        return db

    def return_connection(self, db):
        return self.pool.put_nowait(db)

    def ping(self, db):
        data = db.query('SELECT 1', [])
        return data
