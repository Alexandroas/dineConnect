# Generated by Django 4.2.16 on 2024-10-28 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gfgauth', '0002_alter_business_cuisine'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='business',
            options={'ordering': ['business_name'], 'verbose_name': 'business', 'verbose_name_plural': 'businesses'},
        ),
    ]
