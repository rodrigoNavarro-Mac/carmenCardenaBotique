from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import User


class UserAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="Contrasena",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Dejalo vacio para conservar la contrasena actual.",
    )
    password_confirm = forms.CharField(
        label="Confirmar contrasena",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "role",
            "assigned_branch",
            "is_active",
            "is_staff",
        ]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "username": "Usuario",
            "email": "Correo",
            "phone": "Telefono",
            "role": "Rol",
            "assigned_branch": "Sucursal asignada",
            "is_active": "Activo",
            "is_staff": "Puede entrar al admin Django",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")
        if not self.instance.pk:
            self.fields["password"].required = True
            self.fields["password_confirm"].required = True
            self.fields["password"].help_text = "Minimo 8 caracteres; evita datos obvios."

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password or password_confirm:
            if password != password_confirm:
                self.add_error("password_confirm", "Las contrasenas no coinciden.")
            else:
                validate_password(password, self.instance)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user
