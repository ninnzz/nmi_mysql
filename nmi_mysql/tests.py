import uuid
import nmi_mysql


CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'db': 'nmi_test',   # Assuming there is already a database called nmi_test
    'port': 3306
}


def create_table(db):
    return db.query(
        '''
            CREATE TABLE IF NOT EXISTS users (
                id varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
                name varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
                status enum('active', 'inactive') COLLATE utf8mb4_unicode_ci DEFAULT 'active',
                date_created datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                date_updated datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
    )


def add_users(db, users):
    return db.query(
        '''
            INSERT INTO users (
                id,
                name
            ) VALUES (%s)
        ''',
        users
    )


def select_users(db, params=None):
    if params:
        where_clause = 'WHERE name IN (%s)'

    else:
        where_clause = ''

    return db.query(
        '''
            SELECT  *
            FROM    users
            {}
        '''.format(where_clause),
        params
    )


def update_users(db, params):
    return db.query(
        '''
            UPDATE  users
            SET     %s
            WHERE   name IN (%s)
        ''',
        params
    )


def main():
    db = nmi_mysql.DB(CONFIG)

    result = create_table(db)
    print(result)

    result = add_users(
        db,
        [
            (str(uuid.uuid4()), 'jasper'),
            (str(uuid.uuid4()), 'jv'),
            (str(uuid.uuid4()), 'ninz')
        ]
    )
    print(result)

    result = select_users(
        db,
        [
            ['jasper', 'jv']
        ]
    )
    print(result)

    result = update_users(
        db,
        [
            {'status': 'inactive'},
            ['jasper', 'jv']
        ]
    )
    print(result)

    result = select_users(db)
    print(result)

    (result1, result2, result3) = db.multi_query(
        '''
            SELECT  *
            FROM    users
            WHERE   status = %s;

            SELECT  *
            FROM    users
            WHERE   status = %s;

            UPDATE  users
            SET     status = %s
            WHERE   name IN (%s);
        ''',
        [
            'active',
            'inactive',
            'active',
            ['ninz', 'jv', 'jasper']
        ]
    )
    print(result1)
    print(result2)
    print(result3)


if __name__ == '__main__':
    main()
