# Generated by Django 4.1 on 2022-11-17 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0016_delete_systemuser"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="assignedindicator",
            unique_together={("indicator", "assigned_to_organisation")},
        ),
        migrations.RemoveField(
            model_name="assignedindicator",
            name="assigned_to_member_state",
        ),
    ]
