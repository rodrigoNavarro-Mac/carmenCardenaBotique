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
