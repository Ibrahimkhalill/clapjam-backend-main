# Generated by Django 5.2.1 on 2025-06-02 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postevent',
            old_name='event_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='postevent',
            old_name='event_time',
            new_name='time',
        ),
    ]
