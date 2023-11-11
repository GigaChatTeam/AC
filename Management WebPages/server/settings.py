from decouple import config


SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=list[str])

ROOT_URLCONF = 'server.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
