from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('vendor', 'Vendor'),
        ('customer', 'Customer')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    pending_vendor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
