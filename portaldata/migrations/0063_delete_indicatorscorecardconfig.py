# Generated by Django 4.1 on 2023-04-21 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "portaldata",
            "0062_alter_indicator_data_type_alter_indicator_focus_area_and_more",
        ),
    ]

    operations = [
        migrations.DeleteModel(
            name="IndicatorScoreCardConfig",
        ),
    ]