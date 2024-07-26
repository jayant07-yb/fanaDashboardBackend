# Generated by Django 5.0.7 on 2024-07-26 18:03

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FanaCallRequest",
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
                    "request_type",
                    models.CharField(
                        choices=[
                            ("call_waiter", "Call Waiter"),
                            ("bring_bill", "Bring Bill"),
                            ("order", "Order"),
                            ("bring_water", "Bring Water"),
                        ],
                        max_length=20,
                    ),
                ),
                ("table_id", models.CharField(max_length=20)),
                ("timestamp", models.DateTimeField()),
            ],
        ),
    ]
