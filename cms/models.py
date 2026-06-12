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
