# Generated by Django 4.2.16 on 2024-12-10 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Restaurant_handling', '0014_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='dish',
            name='allergens',
            field=models.ManyToManyField(blank=True, related_name='dishes', to='Restaurant_handling.dieterypreference'),
        ),
    ]