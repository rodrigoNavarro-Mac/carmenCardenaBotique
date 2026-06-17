# Generated for rental delivery/return timestamps.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rentals", "0001_initial"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="rentalreservation",
            new_name="rentals_ren_code_2973f5_idx",
            old_name="rentals_ren_code_b60487_idx",
        ),
        migrations.RenameIndex(
            model_name="rentalreservation",
            new_name="rentals_ren_status_ec0ba8_idx",
            old_name="rentals_ren_status_843fb5_idx",
        ),
        migrations.RenameIndex(
            model_name="rentalreservationline",
            new_name="rentals_ren_product_d241dc_idx",
            old_name="rentals_ren_product_3b03a5_idx",
        ),
        migrations.AddField(
            model_name="rentalreservation",
            name="rented_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="rentalreservation",
            name="returned_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
