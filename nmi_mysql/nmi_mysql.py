"""
    Custom mysql wrapper for pymysql
    Usefull for raw queries and scripting
"""

import re
import logging
import pymysql.cursors
from datetime import datetime


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

        """
            replace all instances of ? to %s la :D YOLO programming best!
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
                    result = { 'affected_rows': cursor.rowcount }
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

    def handle_val(self, temp):
        if isinstance(temp, str):
            return self.handle.escape(temp.replace('%', '%%'))

        else:
            return self.handle.escape(temp)

    def to_string(self, temp):        
        if isinstance(temp, (list, tuple)):
            _tmp = ', '.join([self.handle_val(t) for t in temp])
            return '(' + _tmp + ')' if isinstance(temp, tuple) else _tmp
        
        return self.handle_val(temp)
