# Generated by Django 5.0.6 on 2024-05-27 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("food", "0003_product_order_orderitem"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Item",
        ),
        migrations.RemoveField(
            model_name="product",
            name="stock",
        ),
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True),
        ),
    ]
