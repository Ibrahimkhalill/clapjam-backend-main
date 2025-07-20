from django_setup import *
import subprocess

# if input('Run server with daphne at 0.0.0.0:5959? (yes/no): ').lower() == 'yes':
if True:
    subprocess.run('daphne -b 0.0.0.0 -p 5959 cj.asgi:application', shell=True)