from django_setup import *
import subprocess

print('Updating requirements.txt file...')
subprocess.run('pip freeze > requirements.txt', shell=True)
print('Updated.')
# subprocess.run('cat ./requirements.txt', shell=True)