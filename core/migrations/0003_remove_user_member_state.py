# Generated by Django 4.1 on 2022-11-16 12:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_user_member_state_alter_user_first_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="member_state",
        ),
    ]
