# Generated by Django 4.2.16 on 2024-10-30 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Restaurant_handling', '0006_dieterypreference'),
        ('gfgauth', '0004_customuser_favourite_restaurants'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='dietery_preferences',
            field=models.ManyToManyField(blank=True, related_name='users', to='Restaurant_handling.dieterypreference'),
        ),
    ]
