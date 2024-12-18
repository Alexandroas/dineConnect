# Generated by Django 4.2.16 on 2024-11-05 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Restaurant_handling', '0009_alter_reservation_reservation_date_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='reservation_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20),
        ),
    ]
