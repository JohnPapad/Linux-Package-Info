# Generated by Django 3.2.5 on 2022-02-05 03:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20220205_0022'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='package',
            options={'ordering': ['name', 'distro']},
        ),
    ]
