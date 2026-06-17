from django.db import migrations, models
import django.core.validators


def seed_color_palettes(apps, schema_editor):
    ColorPalette = apps.get_model("cms", "ColorPalette")
    palettes = [
        {
            "name": "Carmen clasica",
            "primary": "#c38380",
            "primary_hover": "#4b342c",
            "primary_contrast": "#fffaf2",
            "accent": "#9c7164",
            "accent_soft": "#ead5c8",
            "paper": "#e8e1d1",
            "surface": "#fbf6eb",
            "surface_muted": "#eee3d2",
            "surface_strong": "#4b342c",
            "ink": "#2f211c",
            "ink_soft": "#9c7164",
            "line": "#cdb9a9",
            "gold": "#d8b69f",
            "rose_soft": "#ead9cf",
            "is_active": True,
            "is_preset": True,
        },
        {
            "name": "Editorial marfil",
            "primary": "#8f5d5a",
            "primary_hover": "#2f2825",
            "primary_contrast": "#fffaf2",
            "accent": "#b18a63",
            "accent_soft": "#eadfcc",
            "paper": "#f2eadf",
            "surface": "#fffaf2",
            "surface_muted": "#e8dccd",
            "surface_strong": "#3a302b",
            "ink": "#2b2420",
            "ink_soft": "#7c6b5c",
            "line": "#d4c2ae",
            "gold": "#c49a68",
            "rose_soft": "#ead6d2",
            "is_active": False,
            "is_preset": True,
        },
        {
            "name": "Nocturna boutique",
            "primary": "#d39a83",
            "primary_hover": "#f0d7c6",
            "primary_contrast": "#231c1a",
            "accent": "#bfa37a",
            "accent_soft": "#463932",
            "paper": "#1f1a18",
            "surface": "#2b2421",
            "surface_muted": "#3a302c",
            "surface_strong": "#e8d5c8",
            "ink": "#f8efe8",
            "ink_soft": "#d2bfb1",
            "line": "#5b4a42",
            "gold": "#d6b37b",
            "rose_soft": "#49322e",
            "is_active": False,
            "is_preset": True,
        },
    ]
    for palette in palettes:
        name = palette.pop("name")
        ColorPalette.objects.update_or_create(name=name, defaults=palette)


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0003_landing_blocks"),
    ]

    operations = [
        migrations.CreateModel(
            name="ColorPalette",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80, unique=True)),
                (
                    "primary",
                    models.CharField(
                        default="#c38380",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "primary_hover",
                    models.CharField(
                        default="#4b342c",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "primary_contrast",
                    models.CharField(
                        default="#fffaf2",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "accent",
                    models.CharField(
                        default="#9c7164",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "accent_soft",
                    models.CharField(
                        default="#ead5c8",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "paper",
                    models.CharField(
                        default="#e8e1d1",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "surface",
                    models.CharField(
                        default="#fbf6eb",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "surface_muted",
                    models.CharField(
                        default="#eee3d2",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "surface_strong",
                    models.CharField(
                        default="#4b342c",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "ink",
                    models.CharField(
                        default="#2f211c",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "ink_soft",
                    models.CharField(
                        default="#9c7164",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "line",
                    models.CharField(
                        default="#cdb9a9",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "gold",
                    models.CharField(
                        default="#d8b69f",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "rose_soft",
                    models.CharField(
                        default="#ead9cf",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Usa un color hexadecimal valido, por ejemplo #C38380.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                ("is_active", models.BooleanField(default=False)),
                ("is_preset", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-is_active", "name"],
            },
        ),
        migrations.RunPython(seed_color_palettes, migrations.RunPython.noop),
    ]
