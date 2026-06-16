from django.db import models

from core.models import TimeStampedModel


class LandingConfig(TimeStampedModel):
    boutique_name = models.CharField(max_length=120, default="Carmen Cardena Boutique")
    headline = models.CharField(max_length=180, default="Moda seleccionada para cada ocasion")
    subheadline = models.TextField(blank=True)
    whatsapp_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.boutique_name


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
