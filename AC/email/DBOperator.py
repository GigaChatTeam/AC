import datetime

import psycopg2

connection = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')


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
            id = %s AND
            intentions = ARRAY['CONFIRM', 'EMAIL'] AND
            blocked IS NULL
        ''', (datetime.datetime.now(), id))

    connection.commit()
