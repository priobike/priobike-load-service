# Generated by Django 5.0.2 on 2024-02-15 10:06

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Start',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'App start',
                'verbose_name_plural': 'App starts',
            },
        ),
    ]
