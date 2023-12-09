from decouple import config

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=list[str])

ROOT_URLCONF = 'server.urls'

SERVER_ID = config("SERVER_ID")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("DB_NAME"),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': config("DB_HOST"),
        'PORT': config("DB_PORT", cast=int),
        'APPLICATION': config("APPLICATION").format(id=SERVER_ID),
    }
}

MIDDLEWARE = [
    'django_ratelimit.middleware.RatelimitMiddleware'
]

RATELIMIT_VIEW = "server.urls.ratelimited"
