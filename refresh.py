import subprocess


print('\nInstalling necessary packages with pip...')
subprocess.run('pip install -r requirements.txt', shell=True)

from django_setup import *

if input('\nStage Migration? (yes/no): ').lower() == 'yes':
    subprocess.run('python manage.py makemigrations', shell=True)
    if input('\nMigrate? (yes/no): ').lower() == 'yes':
        subprocess.run('python manage.py migrate', shell=True)


