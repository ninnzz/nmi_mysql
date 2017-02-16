==========
nmi_mysql
==========

A simple and intuative mysql client wrapper for sqlalchemy.
Ideal for performing simple and raw operations in mysql.

**Installation:**
*pip install nmi_mysql*

**Dependencies**
    * Python 3.4+
    * sqlalchemy (http://www.sqlalchemy.org/)
    * pymysql (http://www.pymysql.org/)

**Change Log**
    * v.0.75
        * Added deprecated warnings
    * v.0.74
        * Automatically closes the connection and connects every query
    * v.0.72
        * Fixed showing of SQLAlchemy Error instead of generic error message
    * v.0.71
        * Added connection polling
        * Used sql alchemy core
        * Updated examples for database operations
    * v.0.63
	* removed unecessary error message upon close
	* raise error instead of returning None
    * v.0.62
        * returns affected rows when executing insert and update
        * defaults the return type for select to lists
    * v.0.61
        * fixed logging issues
    * v.0.58
        * added execute many
        * verified test for logger
    * v.0.57
        * fixed bug on type checking
    * v.0.56
        * updated base code for connection
        * added new docs
    * v.0.55
        * fixed null being converted to string
        * updated docs for examples

For full documentation and usage:
https://github.com/pprmint/nmi_mysql/blob/master/README.md 
