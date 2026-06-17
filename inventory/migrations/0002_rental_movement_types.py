# Generated for rental inventory movement choices.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inventorymovement",
            name="movement_type",
            field=models.CharField(
                choices=[
                    ("IN", "Entrada"),
                    ("SALE", "Venta"),
                    ("RETURN", "Devolucion"),
                    ("TRANSFER_OUT", "Transferencia salida"),
                    ("TRANSFER_IN", "Transferencia entrada"),
                    ("ADJUSTMENT", "Ajuste"),
                    ("WASTE", "Merma"),
                    ("RENTAL_OUT", "Renta salida"),
                    ("RENTAL_RETURN", "Renta devolucion"),
                ],
                max_length=24,
            ),
        ),
    ]
