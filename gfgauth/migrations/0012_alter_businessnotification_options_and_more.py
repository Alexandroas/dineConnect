# Generated by Django 4.2.16 on 2024-11-10 17:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gfgauth', '0011_alter_businesshours_day_of_week_businessnotification'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='businessnotification',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='businessnotification',
            name='notification_date',
        ),
        migrations.RemoveField(
            model_name='businessnotification',
            name='notification_time',
        ),
        migrations.AddField(
            model_name='businessnotification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]