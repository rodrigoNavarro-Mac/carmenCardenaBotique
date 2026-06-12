from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "entity", "entity_id", "user")
    list_filter = ("action", "entity", "created_at")
    search_fields = ("summary", "entity_id")
    readonly_fields = ("created_at",)
