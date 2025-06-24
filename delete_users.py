from django_setup import *
from profiles.models import User

print(User.objects.all().delete())