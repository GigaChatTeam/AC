import datetime

import psycopg2

from . import generator
from .. import settings

connection = psycopg2.connect(
    host=settings.DATABASES['default']['HOST'],
    port=settings.DATABASES['default']['PORT'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    application_name=settings.DATABASES['default']['APPLICATION']
)
connection.autocommit = True


def register(login, password, *, email=None, phone=None):
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO users.accounts (username, password, created)
        VALUES (%s, %s, %s)
        RETURNING id
    ''', (login, generator.Hasher.hash(password).decode(), datetime.datetime.now()))

    try:
        user_id = cursor.fetchone()[0]
    except IndexError:
        return
    else:
        cursor.execute('''
            INSERT INTO users.accounts_changes (client, username, password)
            VALUES (%s, %s, %s)
        ''', (user_id, [datetime.datetime.now()], [datetime.datetime.now()]))

        cursor.execute('''
            INSERT INTO users.confirmations (client, email, phone)
            VALUES (%s, %s, %s)
        ''', (user_id, email, phone))

        return user_id


def auth(login_type, login, password):
    cursor = connection.cursor()

    match login_type:
        case 'username':
            cursor.execute('''
                SELECT password
                FROM users.accounts
                WHERE
                    username = %s
            ''', (login,))
        case 'email':
            cursor.execute('''
                SELECT password
                FROM users.accounts
                WHERE
                    email = %s
            ''', (login,))
        case 'phone':
            cursor.execute('''
                SELECT password
                FROM users.accounts
                WHERE
                    phone = %s
            ''', (login,))
        case _:
            raise ValueError('Invalid type')

    try:
        return generator.Hasher.verify(password, cursor.fetchone()[0].encode())
    except TypeError:
        return None


def check(login_type: str, login: str) -> bool:
    cursor = connection.cursor()

    match login_type:
        case 'username':
            cursor.execute('''
                SELECT id
                FROM users.accounts
                WHERE
                    username = %s
            ''', (login,))
        case 'email':
            cursor.execute('''
                SELECT client
                FROM users.confirmations
                WHERE
                    email = %s
            ''', (login,))
        case 'phone':
            cursor.execute('''
                SELECT client
                FROM users.confirmations
                WHERE
                    phone = %s
            ''', (login,))

    try:
        return bool(cursor.fetchone())
    except TypeError:
        return False


def create_token(agent, id):
    cursor = connection.cursor()

    secret, key = generator.gen_token()

    token = f'user.{id}.{secret}%{key}'

    cursor.execute('''
        INSERT INTO users.tokens (client, agent, secret, key, start)
        VALUES (%s, %s, %s, %s, %s)
    ''', (
        id,
        agent,
        generator.Hasher.hash(secret).decode(),
        generator.Hasher.hash(key).decode(),
        datetime.datetime.now())
    )

    return token


def get_id(username):
    cursor = connection.cursor()

    cursor.execute('''
        SELECT id
        FROM users.accounts
        WHERE
            username = %s
    ''', (username,))

    try:
        return cursor.fetchone()[0]
    except TypeError:
        return None
