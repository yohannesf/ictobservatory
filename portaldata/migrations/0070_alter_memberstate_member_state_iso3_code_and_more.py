# Generated by Django 4.1 on 2023-05-29 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0069_memberstate_member_state_iso3_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="memberstate",
            name="member_state_iso3_code",
            field=models.CharField(blank=True, max_length=3, verbose_name="ISO 3 Code"),
        ),
        migrations.AlterField(
            model_name="memberstate",
            name="member_state_short_name",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="Short Name"
            ),
        ),
        migrations.AlterField(
            model_name="memberstate",
            name="memberstate_status",
            field=models.BooleanField(
                choices=[(True, "Active"), (False, "Inactive")],
                default=True,
                verbose_name="Status",
            ),
        ),
    ]
