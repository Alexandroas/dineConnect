# Generated by Django 4.2.16 on 2024-11-14 21:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_alter_reservation_reservation_status'),
        ('gfgauth', '0015_remove_business_business_max_table_size_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0003_alter_payment_options_payment_ip_address_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={},
        ),
        migrations.RemoveIndex(
            model_name='payment',
            name='payments_pa_user_id_7a85fd_idx',
        ),
        migrations.RemoveIndex(
            model_name='payment',
            name='payments_pa_stripe__6fe52c_idx',
        ),
        migrations.RemoveIndex(
            model_name='payment',
            name='payments_pa_status_7ad4af_idx',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='ip_address',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='refund_reason',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='refunded_amount',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='user_agent',
        ),
        migrations.AddField(
            model_name='payment',
            name='business',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='gfgauth.business'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.reservation'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(default='pending', max_length=100),
        ),
        migrations.AlterField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL),
        ),
    ]