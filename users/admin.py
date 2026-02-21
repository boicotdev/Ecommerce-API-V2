from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm

from .models import User, UserProfileSettings, ReferralDiscount, NewsletterSubscription


# Crear un formulario para el admin para asegurar que la contraseña se maneje correctamente
class CustomUserChangeForm(ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        # Si se está creando un nuevo usuario o si se cambia la contraseña
        if "password" in self.changed_data:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# Personalizar el UserAdmin para incluir los campos adicionales
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("avatar", "role", "phone", "referral_code", "referred_by")}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register([UserProfileSettings, ReferralDiscount, NewsletterSubscription])
