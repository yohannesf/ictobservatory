# Generated by Django 4.1 on 2023-05-29 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0067_alter_scorecardconfig_num_denom"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scorecardconfig",
            name="num_denom",
            field=models.CharField(
                blank=True,
                choices=[("num", "Numerator"), ("denom", "Denominator")],
                max_length=50,
                verbose_name="Numerator / Denominator",
            ),
        ),
    ]