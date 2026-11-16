from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        ARTISAN = "artisan", "Artisan"

    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.ARTISAN)
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\+?[0-9\s\-]{7,20}$", "Enter a valid contact number.")],
    )
    business_name = models.CharField(max_length=120, blank=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def display_name(self):
        return self.get_full_name() or self.username
