# Generated by Django 4.1 on 2022-11-16 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0015_alter_systemuser_user"),
    ]

    operations = [
        migrations.DeleteModel(
            name="SystemUser",
        ),
    ]
