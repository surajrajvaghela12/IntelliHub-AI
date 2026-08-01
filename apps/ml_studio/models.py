from django.db import models
from django.conf import settings
from apps.datasets.models import Dataset

class TrainedModel(models.Model):
    MODEL_TYPE_CHOICES = (
        ('REGRESSION', 'Regression'),
        ('CLASSIFICATION', 'Classification'),
        ('CLUSTERING', 'Clustering'),
        ('DIM_REDUCTION', 'Dimensionality Reduction'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ml_models')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPE_CHOICES)
    algorithm = models.CharField(max_length=100)
    target_column = models.CharField(max_length=100, blank=True, default="")
    feature_columns = models.JSONField(default=list)
    metrics = models.JSONField(default=dict)
    accuracy = models.FloatField(default=0.0)  # Primary sorting score (R2 for reg, Acc for clf)
    model_file = models.FileField(upload_to='trained_models/', blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-accuracy', '-created_at']

    @property
    def formatted_accuracy(self):
        acc = float(self.accuracy or 0)
        if acc <= 1.0:
            acc = acc * 100.0
        return f"{acc:.1f}%"

    def __str__(self):
        return f"{self.name} ({self.algorithm}) - {self.formatted_accuracy}"


class PredictionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    model = models.ForeignKey(TrainedModel, on_delete=models.CASCADE, related_name='predictions')
    input_data = models.JSONField(default=dict)
    prediction_result = models.CharField(max_length=255)
    confidence_score = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction by {self.user.username} using {self.model.name}: {self.prediction_result}"
