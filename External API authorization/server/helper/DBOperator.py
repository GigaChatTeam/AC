import datetime

import psycopg2

from . import generator


connection = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')


def register(login, password, *, email=None, phone=None):
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO public.accounts (username, password, created, email, phone)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id''', (login, generator.Hasher.hash(password).decode(), datetime.datetime.now(), email, phone))

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
                SELECT id
                FROM public.accounts
                WHERE
                    email = %s
            ''', (login,))
        case 'phone':
            cursor.execute('''
                SELECT id
                FROM public.accounts
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


def auth_token(id, token):
    cursor = connection.cursor()

    cursor.execute('''
        SELECT token
        FROM public.tokens
        WHERE
            client = %s
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
        FROM public.accounts
        WHERE
            username = %s
    ''', (username,))

    try:
        return cursor.fetchone()[0]
    except TypeError:
        return None


class TokensControl:
    @staticmethod
    def get_valid_tokens(client):
        cursor = connection.cursor()

        cursor.execute(f'''
            WITH logins AS (
                SELECT logins
                FROM public.tokens
                WHERE
                    client = %s
            )
            
            SELECT
                agent, start,
                (logins[array_upper(logins, 1)] ->> 'time')::TIMESTAMP,
                (logins[array_upper(logins, 1)] ->> 'address')::CIDR
            FROM public.tokens
            WHERE
                client = %s AND
                ending IS NULL
        ''', (client, client))

        return cursor.fetchall()

    @staticmethod
    def revoke_token(client, *, method='OR', token=None, agent=None, time=None):
        if method != 'OR' and method != 'AND':
            raise ValueError

        cursor = connection.cursor()

        cursor.execute(f'''
            UPDATE public.tokens
            SET
                ending = now()
            WHERE
                client = %s AND
                token = %s {method}
                agent = %s {method}
                time = %s
        ''', (client, token, agent, time))

        connection.commit()

        return cursor.rowcount
