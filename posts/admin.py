from django.contrib import admin
from django.apps import apps


app = apps.get_app_config('posts')

for model in app.get_models():
    admin.site.register(model)
