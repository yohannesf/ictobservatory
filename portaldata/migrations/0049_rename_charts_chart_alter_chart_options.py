# Generated by Django 4.1 on 2023-02-04 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0048_rename_indicatorchartconfig_charts"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Charts",
            new_name="Chart",
        ),
        migrations.AlterModelOptions(
            name="chart",
            options={},
        ),
    ]
