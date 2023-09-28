ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'server.urls'

SECRET_KEY = r'j(y0++vg$zgf9n#$b(&e9-w)sa#5+z41&dzcsz4a_t4)p=8f@e'
DEBUG = True

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

MIDDLEWARE = (
    'django_ratelimit.middleware.RatelimitMiddleware',
)

RATELIMIT_VIEW = 'server.views.ratelimited'
