# Generated by Django 3.2.5 on 2022-01-07 03:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_package_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='size',
        ),
        migrations.AddField(
            model_name='packageversion',
            name='size',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]