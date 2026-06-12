from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        ACCOUNTANT = "ACCOUNTANT", "Contador"
        STORE_ADMIN = "STORE_ADMIN", "Administrador de tienda"
        COLLABORATOR = "COLLABORATOR", "Colaborador"

    role = models.CharField(max_length=24, choices=Role.choices, default=Role.COLLABORATOR)
    assigned_branch = models.ForeignKey(
        "branches.Branch",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    phone = models.CharField(max_length=30, blank=True)

    @property
    def can_access_all_branches(self):
        return self.role == self.Role.ADMIN


class RoleModulePermission(models.Model):
    class Module(models.TextChoices):
        DASHBOARD = "dashboard", "Dashboard"
        CATALOG = "catalog", "Catalogo"
        BRANCHES = "branches", "Sucursales"
        INVENTORY = "inventory", "Inventario"
        SALES = "sales", "Ventas"
        CUSTOMERS = "customers", "Clientes"
        FINANCE = "finance", "Finanzas"
        CMS = "cms", "CMS"
        REPORTS = "reports", "Reportes"
        USERS = "users", "Usuarios y permisos"

    role = models.CharField(max_length=24, choices=User.Role.choices)
    module = models.CharField(max_length=32, choices=Module.choices)
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["role", "module"], name="unique_permission_per_role_module")
        ]
        ordering = ["role", "module"]

    def __str__(self):
        return f"{self.get_role_display()} / {self.get_module_display()}"
