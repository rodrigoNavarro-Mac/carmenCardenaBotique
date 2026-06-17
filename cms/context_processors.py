from django.db import OperationalError, ProgrammingError

from .models import ColorPalette, LandingConfig


def active_color_palette(request):
    try:
        palette = ColorPalette.objects.filter(is_active=True).first()
        branding = LandingConfig.objects.filter(is_active=True).first() or LandingConfig.objects.first()
    except (OperationalError, ProgrammingError):
        palette = None
        branding = None
    return {
        "active_color_palette": palette,
        "active_branding": branding,
    }
