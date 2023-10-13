import datetime

import psycopg2

from . import generator


connection = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')


def register(login, password, *, email=None, phone=None):
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO public.accounts (username, password, created)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id''', (login, generator.Hasher.hash(password).decode(), datetime.datetime.now(), email, phone))

    cursor.execute('''
        INSERT INTO public.confirmations (email, phone)
        VALUES (%s, %s)
        RETURNING id''', (email, phone))

    try:
        id = cursor.fetchone()[0]
    except TypeError:
        return
    else:
        cursor.execute('''
            INSERT INTO public.accounts_changes (client, username, password)
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
                FROM public.accounts
                WHERE
                    username = %s
            ''', (login,))
        case 'email':
            cursor.execute('''
                SELECT password
                FROM public.accounts
                WHERE
                    email = %s
            ''', (login,))
        case 'phone':
            cursor.execute('''
                SELECT password
                FROM public.accounts
                WHERE
                    phone = %s
            ''', (login,))
        case _:
            raise ValueError('Invalid type')

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
                FROM public.accounts
                WHERE
                    username = %s
            ''', (login,))
        case 'email':
            cursor.execute('''
                SELECT client
                FROM public.confirmations
                WHERE
                    email = %s
            ''', (login,))
        case 'phone':
            cursor.execute('''
                SELECT client
                FROM public.confirmations
                WHERE
                    phone = %s
            ''', (login,))

    try:
        return bool(cursor.fetchone())
    except TypeError:
        return False


def create_token(agent, id):
    cursor = connection.cursor()

    token = generator.gen_token(id)

    cursor.execute('''
        INSERT INTO public.tokens (client, agent, token, start)
        VALUES (%s, %s, %s, %s)
    ''', (id, agent, generator.Hasher.hash(token).decode(), datetime.datetime.now()))

    connection.commit()

    return token


def get_id(username):
    cursor = connection.cursor()

    cursor.execute('''
        SELECT id
        FROM public.accounts
        WHERE
            username = %s
    ''', (username,))

    try:
        return cursor.fetchone()[0]
    except TypeError:
        return None
