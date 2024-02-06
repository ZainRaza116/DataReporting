# Generated by Django 4.2.2 on 2023-06-13 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0006_game_remove_catogorie_unique_by_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mopredeem",
            name="category",
        ),
        migrations.RemoveField(
            model_name="mopredeem",
            name="payment_method",
        ),
        migrations.RemoveField(
            model_name="mopredeem",
            name="redeem_list",
        ),
        migrations.RemoveField(
            model_name="mopredeem",
            name="refund",
        ),
        migrations.RemoveField(
            model_name="mopredeem",
            name="send",
        ),
        migrations.CreateModel(
            name="RedeemList",
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
                    "send",
                    models.FloatField(
                        blank=True, default=0.0, null=True, verbose_name="Send"
                    ),
                ),
                (
                    "refund",
                    models.FloatField(
                        blank=True, default=0.0, null=True, verbose_name="Refund"
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        max_length=255,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="data.catogorie",
                        verbose_name="Category",
                    ),
                ),
                (
                    "mops_redeem",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data.mopredeem",
                    ),
                ),
                (
                    "payment_method",
                    models.ForeignKey(
                        max_length=255,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="data.paymentmethod",
                    ),
                ),
            ],
        ),
    ]