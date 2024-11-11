# Generated by Django 4.2.16 on 2024-11-11 12:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Restaurant_handling', '0012_remove_reservation_business_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gfgauth', '0013_delete_businessnotification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('reservation_id', models.AutoField(primary_key=True, serialize=False)),
                ('reservation_date', models.DateField()),
                ('reservation_time', models.TimeField()),
                ('reservation_party_size', models.IntegerField()),
                ('reservation_special_requests', models.TextField(blank=True, max_length=100, null=True)),
                ('reservation_status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
                ('business_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gfgauth.business')),
                ('dish_id', models.ManyToManyField(blank=True, to='Restaurant_handling.dish')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]