# Generated by Django 4.1 on 2022-12-28 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0037_alter_generalindicatordata_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="generalindicatordata",
            unique_together={("general_indicator", "reporting_year")},
        ),
    ]
