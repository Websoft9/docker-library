import os
DATABASES = {
    'default': {
        'ATOMIC_REQUESTS': True,
        'ENGINE': 'awx.main.db.profiled_pg',
        'NAME': os.getenv('APP_DB_POSTGRESQL_NAME'),
        'USER': os.getenv('APP_DB_POSTGRESQL_USER'),
        'PASSWORD': os.getenv('PASSWORD'),
        'HOST': "postgres",
        'PORT': "5432",
    }
}
