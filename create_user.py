from django_setup import *
from interface.auth import AuthHandler

def main():
    is_superuser = input('superuser? (yes/no): ').lower() == 'yes'
    print('Creating superuser\n') if is_superuser else print('Creating user\n')
    AuthHandler().setup_user(
        name = input('Name: '),
        email = input('Email: '),
        password = input('Password: '),
        is_superuser = is_superuser
    )

if __name__ == '__main__':
    main()