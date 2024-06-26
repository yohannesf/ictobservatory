# Generated by Django 4.1 on 2023-02-04 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portaldata", "0050_delete_chart"),
    ]

    operations = [
        migrations.CreateModel(
            name="Chart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("chart_title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                (
                    "chart_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Column Chart"),
                            (1, "Line Chart"),
                            (2, "Stacked Column Chart"),
                            (3, "100% Stacked Column Chart"),
                            (4, "Spiderweb Chart"),
                            (5, "Sunburst Chart"),
                        ]
                    ),
                ),
                ("y_axis_title", models.CharField(blank=True, max_length=100)),
                (
                    "aggregation",
                    models.CharField(
                        blank=True,
                        choices=[("avg", "Average"), ("sum", "Total")],
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="IndicatorChartConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "extra_calculation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("per100", "Calculate Per 100"),
                            ("exchangerate", "Convert Currency to USD"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "chart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="portaldata.chart",
                    ),
                ),
                (
                    "indicator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="portaldata.indicator",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="chart",
            name="indicators_list",
            field=models.ManyToManyField(
                through="portaldata.IndicatorChartConfig", to="portaldata.indicator"
            ),
        ),
    ]
