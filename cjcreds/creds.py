PROJECT_SECRET_KET = 'django-insecure-=$w7mvsybo@-24ej1t9hubumim!pfk_$hs=fa3e1bkx)%0bmw!'
MYSQL_DB_ENGINE = 'django.db.backends.mysql'
POSTGRES_DB_ENGINE = 'django.db.backends.postgresql'
MYSQL_DB_NAME = 'clapjam'
POSTGRES_DB_NAME = 'clapjam'
MYSQL_DB_HOST = '127.0.0.1'
POSTGRES_DB_HOST = 'localhost'
POSTGRES_DB_PORT = '5432'
MYSQL_DB_PORT = '3306'
MYSQL_DB_USER = 'root'
POSTGRES_DB_USER = 'postgres'
MYSQL_DB_PASSWORD = 'make_strong_password(mysql)'
POSTGRES_DB_PASSWORD = 'alone'
MYSQL_DB_OPTIONS = {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'" , 'charset': 'utf8mb4'}
POSTGRES_DB_SETUP = {
        'ENGINE': POSTGRES_DB_ENGINE,
        'NAME': POSTGRES_DB_NAME,
        'HOST': POSTGRES_DB_HOST,
        'PORT': POSTGRES_DB_PORT,
        'USER': POSTGRES_DB_USER,
        'PASSWORD': POSTGRES_DB_PASSWORD
}
MYSQL_DB_SETUP = {
        'ENGINE': MYSQL_DB_ENGINE,
        'NAME': MYSQL_DB_NAME,
        'HOST': MYSQL_DB_HOST,
        'PORT': MYSQL_DB_PORT,
        'USER': MYSQL_DB_USER,
        'PASSWORD': MYSQL_DB_PASSWORD,
        'OPTIONS': MYSQL_DB_OPTIONS
    }
