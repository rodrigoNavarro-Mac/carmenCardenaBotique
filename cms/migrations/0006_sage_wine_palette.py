# Generated for the sage and wine boutique palette.

import django.core.validators
from django.db import migrations, models


NEW_PALETTE = {
    "primary": "#6f2d3b",
    "primary_hover": "#2b1821",
    "primary_contrast": "#fffdf8",
    "accent": "#7c8a78",
    "accent_soft": "#e0e7de",
    "paper": "#f7f3ed",
    "surface": "#fffdf8",
    "surface_muted": "#ebe5dc",
    "surface_strong": "#2b1821",
    "ink": "#161411",
    "ink_soft": "#625d55",
    "line": "#d7cec1",
    "gold": "#c7a66a",
    "rose_soft": "#ead8dc",
}

HEX_VALIDATOR = django.core.validators.RegexValidator(
    regex="^#[0-9A-Fa-f]{6}$",
    message="Usa un color hexadecimal valido, por ejemplo #C38380.",
)


def update_active_palette(apps, schema_editor):
    ColorPalette = apps.get_model("cms", "ColorPalette")
    active = ColorPalette.objects.filter(is_active=True).first()
    if active:
        for field, value in NEW_PALETTE.items():
            setattr(active, field, value)
        active.name = "Sage Wine Boutique"
        active.save(update_fields=[*NEW_PALETTE.keys(), "name", "updated_at"])
        return
    ColorPalette.objects.create(name="Sage Wine Boutique", is_active=True, is_preset=True, **NEW_PALETTE)


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0005_landingconfig_logo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="colorpalette",
            name="accent",
            field=models.CharField(default="#7c8a78", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="accent_soft",
            field=models.CharField(default="#e0e7de", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="gold",
            field=models.CharField(default="#c7a66a", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="ink",
            field=models.CharField(default="#161411", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="ink_soft",
            field=models.CharField(default="#625d55", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="line",
            field=models.CharField(default="#d7cec1", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="paper",
            field=models.CharField(default="#f7f3ed", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="primary",
            field=models.CharField(default="#6f2d3b", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="primary_contrast",
            field=models.CharField(default="#fffdf8", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="primary_hover",
            field=models.CharField(default="#2b1821", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="rose_soft",
            field=models.CharField(default="#ead8dc", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="surface",
            field=models.CharField(default="#fffdf8", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="surface_muted",
            field=models.CharField(default="#ebe5dc", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.AlterField(
            model_name="colorpalette",
            name="surface_strong",
            field=models.CharField(default="#2b1821", max_length=7, validators=[HEX_VALIDATOR]),
        ),
        migrations.RunPython(update_active_palette, migrations.RunPython.noop),
    ]
