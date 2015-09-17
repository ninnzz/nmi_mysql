nmi-mysql
=======================

A very simple and intuative mysql client wrapper for pymysql.

## Installation
----------------------

- Run the command to install: `pip install nmi_mysql`
- Make sure you install `pymysql`. You can check out the instructions [here](http://www.pymysql.org/)

## Usage
----------------------

*SELECT operations*
```python

from nmi_mysql import nmi_mysql

connection = nmi_mysql.DB(conf, True)

data1 = connection.query('SELECT * FROM mytable WHERE name = %s', ['ninz'])
data2 = connection.query('SELECT * FROM mytable WHERE name IN (%s) AND age = %s', [['john', 'doe'], 10])

connection.close()
print(data)
print(data2)

```
