# Generated by Django 4.2.16 on 2024-11-04 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Restaurant_handling', '0007_alter_reservation_reservation_special_requests'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='dish_id',
            field=models.ManyToManyField(blank=True, to='Restaurant_handling.dish'),
        ),
    ]
