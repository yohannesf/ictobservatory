# Generated by Django 4.1 on 2022-11-08 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0007_memberstate_memberstate_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="memberstate",
            name="memberstate_status",
        ),
    ]
