# Generated by Django 5.2.1 on 2025-05-17 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_alter_productreview_responses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productreview',
            name='response',
        ),
        migrations.AlterField(
            model_name='productreview',
            name='responses',
            field=models.ManyToManyField(blank=True, related_name='user_responses', to='reviews.reviewresponse'),
        ),
    ]
