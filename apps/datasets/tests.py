from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.datasets.models import Dataset, DatasetVersion
from apps.datasets.utils import analyze_dataset_metadata

User = get_user_model()

class DatasetManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teststudent', password='password123', role='STUDENT')
        
    def test_student_quota_limit(self):
        self.assertEqual(self.user.max_datasets_allowed, 5)
        self.assertTrue(self.user.can_upload_dataset)
        
        # Create 5 datasets
        for i in range(5):
            Dataset.objects.create(user=self.user, name=f"Dataset {i}")
            
        self.assertFalse(self.user.can_upload_dataset)

    def test_dataset_versioning(self):
        ds = Dataset.objects.create(user=self.user, name="Sales Data")
        v1 = DatasetVersion.objects.create(dataset=ds, version_number=1, row_count=100)
        v2 = DatasetVersion.objects.create(dataset=ds, version_number=2, row_count=150)
        
        self.assertEqual(ds.latest_version.version_number, 2)
        self.assertEqual(ds.latest_version.row_count, 150)
