# Generated for linking rental reservations to customers.

import django.db.models.deletion
from django.db import migrations, models


def link_existing_reservations(apps, schema_editor):
    Customer = apps.get_model("customers", "Customer")
    RentalReservation = apps.get_model("rentals", "RentalReservation")
    for reservation in RentalReservation.objects.filter(customer__isnull=True):
        name = (reservation.customer_name or "").strip()
        phone = (reservation.customer_phone or "").strip()
        if not name:
            continue
        matches = Customer.objects.filter(name__iexact=name, is_active=True).order_by("id")
        customer = matches.filter(phone=phone).first() if phone else None
        customer = customer or matches.first()
        if customer is None:
            customer = Customer.objects.create(
                name=name,
                phone=phone,
                notes="Creado automaticamente desde apartado de renta.",
            )
        elif phone and not customer.phone:
            customer.phone = phone
            customer.save(update_fields=["phone", "updated_at"])
        reservation.customer = customer
        reservation.save(update_fields=["customer"])


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0001_initial"),
        ("rentals", "0002_rental_timestamps_and_index_names"),
    ]

    operations = [
        migrations.AddField(
            model_name="rentalreservation",
            name="customer",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="customers.customer"),
        ),
        migrations.RunPython(link_existing_reservations, migrations.RunPython.noop),
    ]
