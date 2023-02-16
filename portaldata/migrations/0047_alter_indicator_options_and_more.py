# Generated by Django 4.1 on 2023-02-03 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0046_alter_indicatorchartconfig_chart_type"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="indicator",
            options={"ordering": ["pk"]},
        ),
        migrations.AlterField(
            model_name="indicator",
            name="indicator_assigned_to",
            field=models.CharField(
                choices=[("M", "Member States"), ("O", "Organisations"), ("S", "SADC")],
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="indicator",
            name="source",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
