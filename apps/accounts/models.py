from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DATA_SCIENTIST', 'Data Scientist'),
        ('STUDENT', 'Student'),
        ('RESEARCHER', 'Researcher'),
        ('COMPANY', 'Company'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    is_banned = models.BooleanField(default=False)

    @property
    def max_datasets_allowed(self):
        if self.role == 'STUDENT':
            return 5
        return 99999  # Unlimited for others

    @property
    def can_upload_dataset(self):
        if self.role == 'ADMIN' or self.role == 'RESEARCHER' or self.role == 'DATA_SCIENTIST' or self.role == 'COMPANY':
            return True
        # Check current uploaded dataset count
        current_count = self.datasets.count()
        return current_count < self.max_datasets_allowed


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default="")
    education = models.CharField(max_length=150, blank=True, default="")
    company = models.CharField(max_length=150, blank=True, default="")
    github = models.URLField(blank=True, default="")
    linkedin = models.URLField(blank=True, default="")
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    dark_mode = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username} ({self.user.role})"
