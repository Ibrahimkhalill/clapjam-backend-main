# Generated by Django 5.2.1 on 2025-07-15 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pic',
            name='cover_pic_url',
        ),
        migrations.AlterField(
            model_name='pic',
            name='profile_pic_url',
            field=models.ImageField(blank=True, null=True, upload_to='profile'),
        ),
    ]
