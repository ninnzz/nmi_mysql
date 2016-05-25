nmi-mysql
=======================
[![Build Status](https://travis-ci.org/pprmint/nmi_mysql.svg?branch=master)](https://travis-ci.org/pprmint/nmi_mysql)
[![PyPI version](https://badge.fury.io/py/nmi_mysql.svg)](https://badge.fury.io/py/nmi_mysql)
[![Code Health](https://landscape.io/github/pprmint/nmi_mysql/master/landscape.svg?style=flat)](https://landscape.io/github/pprmint/nmi_mysql/master)


A very simple and intuitive mysql client wrapper for pymysql.

## Installation


- Run the command to install: `pip install nmi_mysql`
- Make sure you install `pymysql`. You can check out the instructions [here](http://www.pymysql.org/)

## Usage
Minimal and straightforward when doing queries
- Imports the nmi-mysql client library

```python
from nmi_mysql import nmi_mysql
```

- Initialization: Accepts one parameter, which is the config object

```python
db = nmi_mysql.DB(conf)
```

- Query execution: Accepts two parameters. The first is the query and the second is the list of parameters to be used. See example below

```python
data = db.query(query, params)
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

data1 = db.query('SELECT * FROM mytable WHERE name = %s', ['ninz'])
data2 = db.query('SELECT * FROM mytable WHERE name IN (%s) AND age = %s', [['john', 'doe'], 10])

print(data)
print(data2)
```

##### INSERT operations

```python
from nmi_mysql import nmi_mysql

db = nmi_mysql.DB(conf)

# Throws an error upon failure
try:
    result = db.query('INSERT INTO users VALUES(%s)', [user_object])
except Exception as err:
    print(err)
```
