import datetime

import psycopg2

connection = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')


def save_token(id, token):
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO public.ttokens (client, token, hashed, extradition, intentions)
        VALUES (%s, %s, FALSE, %s, ARRAY['CONFIRM', 'EMAIL'])
    ''', (id, token, datetime.datetime.now()))

    connection.commit()


def verify_token(id, token):
    cursor = connection.cursor()

    cursor.execute('''
        SELECT token
        FROM public.ttokens
        WHERE
            client = 1 AND
            intentions = ARRAY['CONFIRM', 'EMAIL'] AND
            CURRENT_TIMESTAMP - extradition <= INTERVAL '4 hours' AND
            blocked IS NULL
    ''', (id,))

    if token in cursor.fetchall():
        return True
    else:
        return False


def close_tokens(id):
    cursor = connection.cursor()

    cursor.execute('''
        UPDATE public.ttokens
        SET
            blocked = %s,
            reason = 'verification has already been made'
        WHERE
            client = %s AND
            intentions = ARRAY['CONFIRM', 'EMAIL'] AND
            blocked IS NULL
    ''', (datetime.datetime.now(), id))

    connection.commit()
