import os
DATABASES = {
    'default': {
        'ATOMIC_REQUESTS': True,
        'ENGINE': 'awx.main.db.profiled_pg',
        'NAME': os.getenv('POSTGRES_USER'),
        'USER': os.getenv('POSTGRES_DB'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': "postgres",
        'PORT': "5432",
    }
}
