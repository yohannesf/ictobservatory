# Generated by Django 4.1 on 2023-04-21 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0066_rename_extra_calculation_scorecardconfig_num_denom"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scorecardconfig",
            name="num_denom",
            field=models.CharField(
                blank=True,
                choices=[("num", "Numerator"), ("denom", "Denominator")],
                max_length=50,
            ),
        ),
    ]
