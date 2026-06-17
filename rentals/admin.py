from django.contrib import admin

from .models import RentalReservation, RentalReservationLine


class RentalReservationLineInline(admin.TabularInline):
    model = RentalReservationLine
    extra = 0


@admin.register(RentalReservation)
class RentalReservationAdmin(admin.ModelAdmin):
    list_display = ("code", "customer_name", "customer_phone", "status", "expires_at", "created_at")
    search_fields = ("code", "customer_name", "customer_phone")
    list_filter = ("status",)
    inlines = [RentalReservationLineInline]
