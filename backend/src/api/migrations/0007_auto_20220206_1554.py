# Generated by Django 3.2.5 on 2022-02-06 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20220205_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='homepage',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='package',
            name='repo_URL',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='packageversion',
            name='binary_URL',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
    ]
