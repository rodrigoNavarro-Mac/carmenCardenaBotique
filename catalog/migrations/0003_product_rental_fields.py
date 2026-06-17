# Generated for public rental catalog fields.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_product_external_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_rentable",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="rental_deposit",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="rental_price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="rental_terms",
            field=models.CharField(blank=True, max_length=180),
        ),
    ]
