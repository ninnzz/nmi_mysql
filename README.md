nmi-mysql
=======================
[![PyPI version](https://badge.fury.io/py/nmi_mysql.svg)](https://badge.fury.io/py/nmi_mysql)
[![Code Health](https://landscape.io/github/pprmint/nmi_mysql/master/landscape.svg?style=flat)](https://landscape.io/github/pprmint/nmi_mysql/master)


A very simple and intuative mysql client wrapper for pymysql.

## Installation


- Run the command to install: `pip install nmi_mysql`
- Make sure you install `pymysql`. You can check out the instructions [here](http://www.pymysql.org/)

## Usage
Minimal and straightforward when doing queries
- Imports the nmi-mysql client library

```python
from nmi_mysql import nmi_mysql
```
- Initialization: Accepts two parameters, first being the config object and the second specifying if autoconnect to db is enabled. If set to false, call `con.connect()` 

```python
try:
    con = nmi_mysql.DB(conf, True)
except Exception as err:
    print(err)
```
- Query execution: Accepts two parameters. The first is the query and the second is the list of parameters to be used. See example below

```python
data = con.query(query, params)
```
- Closing connection

```python
con.close()
```

**Sample config object**
```python
conf = {
    'host': 'localhost',
    'user': 'root',
    'password':'',
    'db': 'mydb',
    'port': 3306    
}
```

##### SELECT operations
```python
from nmi_mysql import nmi_mysql

connection = nmi_mysql.DB(conf, True)

data1 = connection.query('SELECT * FROM mytable WHERE name = %s', ['ninz'])
data2 = connection.query('SELECT * FROM mytable WHERE name IN (%s) AND age = %s', [['john', 'doe'], 10])

connection.close()

print(data)
print(data2)

```

##### INSERT operations
```python
from nmi_mysql import nmi_mysql

connection = nmi_mysql.DB(conf, True)

# Throws an error upon failure
try:
    result = connection.query('INSERT INTO users VALUES(%s)', [user_object])
except Exception as err:
    print(err)
connection.close()
```
