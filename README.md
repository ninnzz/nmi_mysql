nmi-mysql
=======================
[![Build Status](https://travis-ci.org/pprmint/nmi_mysql.svg?branch=master)](https://travis-ci.org/pprmint/nmi_mysql)
[![PyPI version](https://badge.fury.io/py/nmi_mysql.svg)](https://badge.fury.io/py/nmi_mysql)
[![Code Health](https://landscape.io/github/pprmint/nmi_mysql/master/landscape.svg?style=flat)](https://landscape.io/github/pprmint/nmi_mysql/master)


A very simple and intuitive mysql client wrapper for sqlalchemy.

## Installation

- Install [`sqlalchemy`](http://www.sqlalchemy.org/)
- Install [`pymysql`](http://www.pymysql.org/) as it is the MySQL driver used by `nmi_mysql`
  - PyMySQL References:
    - https://gist.github.com/methane/90ec97dda7fa9c7c4ef1
    - https://wiki.openstack.org/wiki/PyMySQL_evaluation
- Run the command to install: `pip install nmi_mysql`

## Usage

Minimal and straightforward when doing queries

- Import the nmi-mysql client library

```python
from nmi_mysql import nmi_mysql
```

- Initialization: Requires a parameter, config object, and has optional parameter, autoconnect (boolean)

```python
db = nmi_mysql.DB(conf)     # can be db = nmi_mysql.DB(conf, True) to auto-connect, default is False or do not connect
```

- Connection: Has optional parameter, retry (integer)

```python
db.connect()    # can be db.connect(5) to retry connecting 5 times, default is 0 or do no retry
```

- Query execution: Accepts two parameters. The first is the query and the second is the list of parameters to be used

```python
data = db.query(query, params)
```

- Closing connection

```python
db.close()
```

**Sample config object**

```python
conf = {
    'host': 'localhost',
    'user': 'root',
    'password':'',
    'db': 'mydb',
    'port': 3306,
    'max_pool_size': 20     # optional, default is 10
}
```

##### SELECT operations

```python
from nmi_mysql import nmi_mysql

db = nmi_mysql.DB(conf)
db.connect()

data1 = db.query('SELECT * FROM users WHERE name = %s', ['ninz'])
data2 = db.query('SELECT * FROM users WHERE name IN (%s) AND age = %s', [['john', 'doe'], 10])

print(data)
print(data2)

db.close()
```

##### INSERT operations

```python
from nmi_mysql import nmi_mysql

db = nmi_mysql.DB(conf)
db.connect()

# Throws an error upon failure
try:
    result = db.query('INSERT INTO users(id, name) VALUES (%s)', [(1, 'jasper'), (2, 'jv')])
except Exception as err:
    print(err)

db.close()
```

##### UPDATE operations

```python
from nmi_mysql import nmi_mysql

db = nmi_mysql.DB(conf)
db.connect()

result1 = db.query('UPDATE users SET %s WHERE name = %s', [{'name': 'ninz'}, 'jasper'])
result2 = db.query('UPDATE users SET name = %s WHERE id IN (%s)', ['sherwin', [1, 2]])

db.close()
```

##### Multiple statements in a single query

```python
from nmi_mysql import nmi_mysql

db = nmi_mysql.DB(conf)
db.connect()

results = db.query('SELECT * FROM users WHERE status = %s; SELECT * FROM users WHERE status = %s', ['active', 'inactive'])

print(results)
```
