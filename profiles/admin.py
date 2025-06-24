from django.contrib import admin
from . import models

admin.site.register([
    models.Country,
    models.City,
    models.BirthDate,
    models.Address,
    models.AuthCode,
    models.Pic,
    models.Nickname,
    models.Bio
])
