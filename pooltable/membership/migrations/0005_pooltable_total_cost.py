# Generated by Django 4.2 on 2023-04-27 08:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("membership", "0004_pooltable_total_paused_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="pooltable",
            name="total_cost",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=8,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
    ]