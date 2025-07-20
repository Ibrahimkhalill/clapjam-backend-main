import subprocess

# command = lambda cmd: list(cmd.split())
command = lambda cmd: cmd

subprocess.run(command('pip freeze > requirements.txt'), shell=True)
print('requiremnts.txt file is updated.')
# subprocess.run('chcp 65001', shell=True)
# file = open('data.json', 'w', encoding='utf-8'); file.close()
# subprocess.run(command('python manage.py dumpdata > data.json'), shell=True)
# print('data.json file is updated.')
subprocess.run(command('git init'), shell=True)
print('git initiated...')
subprocess.run(command('git add .'), shell=True)
print('staged files to commit.')
msg = input('commit message: ')
subprocess.run(command(f'git commit -m "{msg}"'), shell=True)
print('committed with msg: ', msg)
subprocess.run(command('git push origin main'), shell=True)
print('pushed to main!')