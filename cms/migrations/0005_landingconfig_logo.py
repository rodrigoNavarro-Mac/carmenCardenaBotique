from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0004_colorpalette"),
    ]

    operations = [
        migrations.AddField(
            model_name="landingconfig",
            name="logo_alt_text",
            field=models.CharField(blank=True, max_length=140),
        ),
        migrations.AddField(
            model_name="landingconfig",
            name="logo_external_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="landingconfig",
            name="logo_image",
            field=models.ImageField(blank=True, upload_to="branding/"),
        ),
    ]
