# Generated by Django 5.2.1 on 2025-05-21 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_payment_currency_id_payment_external_reference_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_id',
            field=models.BigIntegerField(default=0, unique=True),
        ),
    ]
