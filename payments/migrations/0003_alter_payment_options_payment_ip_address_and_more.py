# Generated by Django 4.2.16 on 2024-11-13 13:03

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reservations', '0001_initial'),
        ('payments', '0002_alter_payment_reservation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='payment',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='refund_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='refunded_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='payments', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='user_agent',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='reservations.reservation'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded'), ('partially_refunded', 'Partially Refunded'), ('cancelled', 'Cancelled')], default='pending', max_length=100),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['user', '-created_at'], name='payments_pa_user_id_7a85fd_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['stripe_payment_intent_id'], name='payments_pa_stripe__6fe52c_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['status'], name='payments_pa_status_7ad4af_idx'),
        ),
    ]
