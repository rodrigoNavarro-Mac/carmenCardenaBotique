# Generated for rental reservations.

import django.core.validators
import django.db.models.deletion
import rentals.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("branches", "0001_initial"),
        ("catalog", "0003_product_rental_fields"),
        ("inventory", "0002_rental_movement_types"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RentalReservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(default=rentals.models.generate_reservation_code, max_length=24, unique=True)),
                ("customer_name", models.CharField(max_length=160)),
                ("customer_phone", models.CharField(max_length=40)),
                ("pickup_date", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("PENDING", "Pendiente"), ("EXPIRED", "Vencido"), ("CANCELLED", "Cancelado"), ("RENTED", "Entregado"), ("RETURNED", "Devuelto")], default="PENDING", max_length=16)),
                ("expires_at", models.DateTimeField(default=rentals.models.default_expiration)),
                ("notes", models.TextField(blank=True)),
                ("processed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="processed_rental_reservations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [models.Index(fields=["code"], name="rentals_ren_code_b60487_idx"), models.Index(fields=["status", "expires_at"], name="rentals_ren_status_843fb5_idx")],
            },
        ),
        migrations.CreateModel(
            name="RentalReservationLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ("rental_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("rental_deposit", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="branches.branch")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.product")),
                ("reservation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lines", to="rentals.rentalreservation")),
            ],
            options={
                "indexes": [models.Index(fields=["product", "branch"], name="rentals_ren_product_3b03a5_idx")],
            },
        ),
    ]
