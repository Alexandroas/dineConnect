# Generated by Django 4.2.16 on 2024-11-11 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Restaurant_handling', '0012_remove_reservation_business_id_and_more'),
        ('payments', '0002_alter_payment_reservation'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Reservation',
        ),
    ]
