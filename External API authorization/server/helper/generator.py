from secrets import token_hex, token_urlsafe

import bcrypt


class Hasher:
    @staticmethod
    def hash(data):
        return bcrypt.hashpw(data.encode(), bcrypt.gensalt())

    @staticmethod
    def verify(data, hash):
        return bcrypt.checkpw(data.encode(), hash)


def gen_secret():
    return token_hex(36)


def gen_key():
    return token_urlsafe(36)


def gen_token():
    return gen_secret(), gen_key()
