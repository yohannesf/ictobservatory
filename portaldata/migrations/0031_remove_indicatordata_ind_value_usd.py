# Generated by Django 4.1 on 2022-12-07 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0030_indicatordata_ind_value_adjusted"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="indicatordata",
            name="ind_value_usd",
        ),
    ]
