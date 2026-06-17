from django.db import models
from django.core.validators import RegexValidator

from core.models import TimeStampedModel


hex_color_validator = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="Usa un color hexadecimal valido, por ejemplo #C38380.",
)


class ColorPalette(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    primary = models.CharField(max_length=7, validators=[hex_color_validator], default="#c38380")
    primary_hover = models.CharField(max_length=7, validators=[hex_color_validator], default="#4b342c")
    primary_contrast = models.CharField(max_length=7, validators=[hex_color_validator], default="#fffaf2")
    accent = models.CharField(max_length=7, validators=[hex_color_validator], default="#9c7164")
    accent_soft = models.CharField(max_length=7, validators=[hex_color_validator], default="#ead5c8")
    paper = models.CharField(max_length=7, validators=[hex_color_validator], default="#e8e1d1")
    surface = models.CharField(max_length=7, validators=[hex_color_validator], default="#fbf6eb")
    surface_muted = models.CharField(max_length=7, validators=[hex_color_validator], default="#eee3d2")
    surface_strong = models.CharField(max_length=7, validators=[hex_color_validator], default="#4b342c")
    ink = models.CharField(max_length=7, validators=[hex_color_validator], default="#2f211c")
    ink_soft = models.CharField(max_length=7, validators=[hex_color_validator], default="#9c7164")
    line = models.CharField(max_length=7, validators=[hex_color_validator], default="#cdb9a9")
    gold = models.CharField(max_length=7, validators=[hex_color_validator], default="#d8b69f")
    rose_soft = models.CharField(max_length=7, validators=[hex_color_validator], default="#ead9cf")
    is_active = models.BooleanField(default=False)
    is_preset = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_active", "name"]

    def __str__(self):
        return self.name

    @property
    def css_variable_items(self):
        return [
            ("--color-primary", self.primary),
            ("--color-primary-hover", self.primary_hover),
            ("--color-primary-contrast", self.primary_contrast),
            ("--color-accent", self.accent),
            ("--color-accent-soft", self.accent_soft),
            ("--color-paper", self.paper),
            ("--color-surface", self.surface),
            ("--color-surface-muted", self.surface_muted),
            ("--color-surface-strong", self.surface_strong),
            ("--color-ink", self.ink),
            ("--color-ink-soft", self.ink_soft),
            ("--color-line", self.line),
            ("--color-gold", self.gold),
            ("--color-rose-soft", self.rose_soft),
            ("--color-warning", self.accent),
            ("--color-success", self.surface_strong),
            ("--color-info", self.accent),
        ]


class LandingConfig(TimeStampedModel):
    boutique_name = models.CharField(max_length=120, default="Carmen Cardena Boutique")
    logo_image = models.ImageField(upload_to="branding/", blank=True)
    logo_external_url = models.URLField(blank=True)
    logo_alt_text = models.CharField(max_length=140, blank=True)
    headline = models.CharField(max_length=180, default="Moda seleccionada para cada ocasion")
    subheadline = models.TextField(blank=True)
    whatsapp_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.boutique_name

    @property
    def logo_url(self):
        if self.logo_image:
            return self.logo_image.url
        return self.logo_external_url

    @property
    def logo_alt(self):
        return self.logo_alt_text or self.boutique_name


class GalleryImage(TimeStampedModel):
    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to="gallery/", blank=True)
    external_image_url = models.URLField(blank=True)
    product = models.ForeignKey("catalog.Product", null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey("branches.Branch", null=True, blank=True, on_delete=models.SET_NULL)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title


class LandingPage(TimeStampedModel):
    title = models.CharField(max_length=120, default="Landing principal")
    slug = models.SlugField(max_length=80, unique=True, default="home")
    boutique_name = models.CharField(max_length=120, default="Carmen Cardena Boutique")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class LandingBlock(TimeStampedModel):
    class BlockType(models.TextChoices):
        HERO = "hero", "Hero"
        LOOKBOOK = "lookbook", "Lookbook"
        FEATURED_PRODUCTS = "featured_products", "Productos destacados"
        EDITORIAL = "editorial", "Editorial / beneficios"
        GALLERY = "gallery", "Galeria"
        BRANCHES = "branches", "Sucursales"
        CTA = "cta", "CTA final"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Borrador"
        PUBLISHED = "PUBLISHED", "Publicado"

    page = models.ForeignKey(LandingPage, related_name="blocks", on_delete=models.CASCADE)
    type = models.CharField(max_length=40, choices=BlockType.choices)
    title = models.CharField(max_length=180)
    subtitle = models.CharField(max_length=220, blank=True)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="landing/blocks/", blank=True)
    external_image_url = models.URLField(blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=240, blank=True)
    secondary_cta_label = models.CharField(max_length=80, blank=True)
    secondary_cta_url = models.CharField(max_length=240, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED


class LandingBlockItem(TimeStampedModel):
    block = models.ForeignKey(LandingBlock, related_name="items", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=220, blank=True)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="landing/items/", blank=True)
    external_image_url = models.URLField(blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=240, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title
