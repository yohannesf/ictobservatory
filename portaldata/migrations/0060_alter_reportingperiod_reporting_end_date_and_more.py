# Generated by Django 4.1 on 2023-04-08 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0059_generalindicator_series_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reportingperiod",
            name="reporting_end_date",
            field=models.DateField(verbose_name="Reporting End Date"),
        ),
        migrations.AlterField(
            model_name="reportingperiod",
            name="reporting_start_date",
            field=models.DateField(verbose_name="Reporting Start Date"),
        ),
    ]
