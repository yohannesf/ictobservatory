# Generated by Django 4.1 on 2023-05-29 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0068_alter_scorecardconfig_num_denom"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberstate",
            name="member_state_iso3_code",
            field=models.CharField(blank=True, max_length=3, verbose_name="ISO 3"),
        ),
    ]
