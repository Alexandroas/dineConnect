# Generated by Django 4.2.16 on 2024-12-09 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gfgauth', '0017_alter_business_business_tax_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='business',
            name='business_tax_code',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='business',
            name='contact_number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
