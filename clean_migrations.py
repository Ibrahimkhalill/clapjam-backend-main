from django_setup import *
import os, shutil


if input('Are you sure kafi bhai? (yes/no): ').lower() == 'yes':
    
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

for root, dirs, files in os.walk(PROJECT_ROOT):
    if os.path.basename(root) == "migrations":
        for file in files:
            if file != "__init__.py" and file.endswith(".py"):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            elif file.endswith(".pyc"):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"Deleted folder: {pycache_path}")