from django.db import models
from django.conf import settings
import os

class Dataset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    file_format = models.CharField(max_length=10, default='CSV')
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (by {self.user.username})"

    @property
    def latest_version(self):
        return self.versions.order_by('-version_number').first()

class DatasetVersion(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField(default=1)
    file = models.FileField(upload_to='datasets/')
    row_count = models.IntegerField(default=0)
    column_count = models.IntegerField(default=0)
    memory_usage_bytes = models.BigIntegerField(default=0)
    memory_usage_str = models.CharField(max_length=50, default="0 KB")
    duplicate_rows = models.IntegerField(default=0)
    missing_values = models.IntegerField(default=0)
    numerical_cols = models.IntegerField(default=0)
    categorical_cols = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.dataset.name} - v{self.version_number}"

    def get_file_path(self):
        if self.file:
            return self.file.path
        return ""
