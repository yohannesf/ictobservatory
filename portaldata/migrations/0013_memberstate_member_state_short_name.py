# Generated by Django 4.1 on 2022-11-15 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0012_focusarea_focusarea_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberstate",
            name="member_state_short_name",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
