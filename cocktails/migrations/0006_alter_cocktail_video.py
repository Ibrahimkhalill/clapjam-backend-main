# Generated by Django 5.2.1 on 2025-06-19 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cocktails', '0005_remove_cocktail_receipe_steps_cocktail_recipe_steps_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cocktail',
            name='video',
            field=models.URLField(blank=True, null=True),
        ),
    ]
