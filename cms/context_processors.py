from django.db import OperationalError, ProgrammingError

from .models import LandingConfig


def active_color_palette(request):
    try:
        branding = LandingConfig.objects.filter(is_active=True).first() or LandingConfig.objects.first()
    except (OperationalError, ProgrammingError):
        branding = None
    return {
        "active_color_palette": None,
        "active_branding": branding,
    }
