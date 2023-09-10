import datetime

import psycopg2

from . import generator


connection = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')


def register(login, password, *, email=None, phone=None):
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO accounts (username, password, email, phone)
        VALUES (%s, %s, %s, %s)
    ''', (login, generator.Hasher.hash(password).decode(), email, phone))

    cursor.execute('''
        SELECT id
        FROM accounts
        WHERE username = %s
    ''', (login,))

    try:
        id = cursor.fetchone()[0]
    except TypeError:
        return
    else:
        cursor.execute('''
            INSERT INTO changes (account_id, nickname, password)
            VALUES (%s, %s, %s)
        ''', (id, [datetime.datetime.now()], [datetime.datetime.now()]))

        connection.commit()

        return id


def auth(login_type, login, password):
    cursor = connection.cursor()

    match login_type:
        case 'username':
            cursor.execute('''
                SELECT password
                FROM accounts
                WHERE username = %s
            ''', (login,))
        case 'email':
            cursor.execute('''
                SELECT password
                FROM accounts
                WHERE email = %s
            ''', (login,))
        case 'phone':
            cursor.execute('''
                SELECT password
                FROM accounts
                WHERE phone = %s
            ''', (login,))
        case _:
            raise ValueError(f'Unknown login type: {login_type}')

    try:
        return generator.Hasher.verify(password, cursor.fetchone()[0].encode())
    except TypeError:
        return None


def check(login_type, login):
    cursor = connection.cursor()

    match login_type:
        case 'username':
            cursor.execute('''
                SELECT id
                FROM accounts
                WHERE username = %s
            ''', (login,))
        case 'email':
            cursor.execute('''
                SELECT id
                FROM accounts
                WHERE email = %s
            ''', (login,))
        case 'phone':
            cursor.execute('''
                SELECT id
                FROM accounts
                WHERE phone = %s
            ''', (login,))
        case _:
            raise ValueError(f'Unknown login type: {login_type}')

    try:
        return bool(cursor.fetchone())
    except TypeError:
        return False


def create_token(agent, id):
    cursor = connection.cursor()

    token = generator.gen_token(id)

    cursor.execute('''
        INSERT INTO tokens (account_id, agent, token, start)
        VALUES (%s, %s, %s, %s)
    ''', (id, agent, generator.Hasher.hash(token).decode(), datetime.datetime.now()))

    connection.commit()

    return token


def auth_token(id, token):
    cursor = connection.cursor()

    cursor.execute('''
        SELECT token
        FROM tokens
        WHERE account_id = %s
    ''', (id,))

    try:
        hash = cursor.fetchone()[0]
    except TypeError:
        return False
    else:
        return generator.Hasher.verify(token, hash.encode())


def get_id(username):
    cursor = connection.cursor()

    cursor.execute('''
        SELECT id
        FROM accounts
        WHERE username = %s
    ''', (username,))

    try:
        return cursor.fetchone()[0]
    except TypeError:
        return None
