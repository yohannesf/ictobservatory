# Generated by Django 4.1 on 2022-12-17 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0034_remove_generalindicator_indicator_value_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="generalindicator",
            name="definition",
            field=models.TextField(blank=True),
        ),
    ]
