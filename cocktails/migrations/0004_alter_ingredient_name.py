# Generated by Django 5.2.1 on 2025-06-18 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cocktails', '0003_rename_coctail_bookmark_cocktail_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
