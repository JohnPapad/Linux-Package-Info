# Generated by Django 3.2.5 on 2022-02-08 05:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_package_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='package',
            options={'ordering': ['name', 'distro']},
        ),
    ]
