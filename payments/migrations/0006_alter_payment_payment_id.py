# Generated by Django 5.2.1 on 2025-05-21 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_alter_payment_payment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_id',
            field=models.BigIntegerField(blank=True, null=True, unique=True),
        ),
    ]
