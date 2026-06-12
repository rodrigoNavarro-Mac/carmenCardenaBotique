from django.db import models

from core.models import TimeStampedModel


class Branch(TimeStampedModel):
    name = models.CharField(max_length=120)
    address = models.TextField()
    phone = models.CharField(max_length=30, blank=True)
    responsible_person = models.CharField(max_length=120, blank=True)
    hours = models.CharField(max_length=160, blank=True)
    image = models.ImageField(upload_to="branches/", blank=True)
    maps_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
