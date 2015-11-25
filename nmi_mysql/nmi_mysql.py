"""
    Custom mysql wrapper for pymysql
    Usefull for raw queries and scripting
"""

import re
import logging
import pymysql.cursors

from queue import Queue


class DB():

    def __init__(self, conf, autoconnect=False):
        self.logger = logging.getLogger('database')
        self.host = conf['host']
        self.user = conf['user']
        self.password = conf['password']
        self.db_conn = conf['db']
        self.port = int(conf['port'])
        self.handle = None
        self.connected = False

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
            params = tuple(self.to_string(p) for p in _params)
            query = query % params

        else:
            query = query % self.to_string(_params)

        try:
            with self.handle.cursor() as cursor:
                cursor.execute(query, ())

                if 'insert' in query.lower() or 'update' in query.lower():
                    result = {'affected_rows': cursor.rowcount}
                else:
                    result = list(cursor.fetchall())

        except Exception as err:
            self.logger.warn(query)
            self.logger.warn(err)
            raise err
        
        self.handle.commit()

        return result

    def execute_many(self, _query, _params):
        try:
            with self.handle.cursor() as cursor:
                cursor.executemany(_query, _params)
        except Exception as err:
            self.logger.warn(err)
            raise err

        self.handle.commit()

    def to_string(self, temp):        
        if isinstance(temp, (list, tuple)):
            _tmp = ', '.join([self.to_string(t) for t in temp])
            return '(' + _tmp + ')' if isinstance(temp, tuple) else _tmp
        
        elif isinstance(temp, str):
            return self.handle.escape(temp.replace('%', '%%'))

        else:
            return self.handle.escape(temp)


class ConnectionPool():
    """
    Usage:
        conn_pool = nmi_mysql.ConnectionPool(config)

        db = conn_pool.get_connection()
        db.query('SELECT 1', [])
        conn_pool.return_connection(db)

        conn_pool.close()
    """
    def __init__(self, conf, max_pool_size=20):
        self.conf = conf
        self.max_pool_size = max_pool_size
        self.initialize_pool()

    def initialize_pool(self):
        self.pool = Queue(maxsize=self.max_pool_size)
        for _ in range(0, self.max_pool_size):
            self.pool.put_nowait(DB(self.conf, True))

    def get_connection(self):
        # returns a db instance when one is available else waits until one is
        db = self.pool.get(True)

        # checks if db is still connected because db instance automatically closes when not in used
        if not self.ping(db):
            db.connect()

        return db

    def return_connection(self, db):
        return self.pool.put_nowait(db)

    def close(self):
        while not self.is_empty():
            self.pool.get().close()

    def ping(self, db):
        data = db.query('SELECT 1', [])
        return data

    def get_initialized_connection_pool(self):
        return self.pool

    def is_empty(self):
        return self.pool.empty()
