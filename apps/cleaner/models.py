from django.db import models
from django.conf import settings
from apps.datasets.models import Dataset

class CleaningHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='cleaning_history')
    action_type = models.CharField(max_length=100)
    before_rows = models.IntegerField()
    after_rows = models.IntegerField()
    before_missing = models.IntegerField()
    after_missing = models.IntegerField()
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action_type} on {self.dataset.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
