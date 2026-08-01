import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intellihub.settings')
django.setup()

from apps.accounts.models import User, UserProfile
from apps.datasets.models import Dataset, DatasetVersion
from apps.datasets.utils import analyze_dataset_metadata
from apps.ml_studio.models import TrainedModel
from django.core.files.base import ContentFile
import pandas as pd

def run_seed():
    print("Seeding IntelliHub AI Platform Data...")
    
    # 1. Create Default Users for all SaaS Roles
    users_data = [
        {'username': 'admin', 'email': 'admin@intellihub.ai', 'role': 'ADMIN', 'is_superuser': True, 'is_staff': True},
        {'username': 'datascientist', 'email': 'ds@intellihub.ai', 'role': 'DATA_SCIENTIST'},
        {'username': 'student_user', 'email': 'student@lju.edu.in', 'role': 'STUDENT'},
        {'username': 'researcher', 'email': 'researcher@lju.edu.in', 'role': 'RESEARCHER'},
        {'username': 'company_user', 'email': 'corp@company.com', 'role': 'COMPANY'},
    ]
    
    users_map = {}
    for udata in users_data:
        is_sup = udata.pop('is_superuser', False)
        is_stf = udata.pop('is_staff', False)
        user, created = User.objects.get_or_create(username=udata['username'], defaults=udata)
        if created:
            user.set_password('admin123')
            user.is_superuser = is_sup
            user.is_staff = is_stf
            user.save()
            print(f"Created user: {user.username} ({user.role})")
        users_map[user.role] = user

    admin_user = users_map['ADMIN']

    # 2. Seed Sample Datasets from media/samples/
    samples_dir = os.path.join("media", "samples")
    sample_files = [
        {'name': 'Car Sales Price Dataset', 'file': 'car_data.csv', 'desc': 'Car selling prices, kilometers driven, fuel types, and transmission data (Syllabus Practical 1-4).'},
        {'name': 'Student Performance Dataset', 'file': 'students.csv', 'desc': 'Student study hours, attendance %, exam scores, gender, and result status (Syllabus Practical 3).'},
        {'name': 'Supermarket Sales Dataset', 'file': 'supermarket_sales.csv', 'desc': 'Supermarket sales transactions by branch, city, product line, payment method, and ratings (Syllabus Practical 4).'},
    ]

    for s in sample_files:
        fpath = os.path.join(samples_dir, s['file'])
        if os.path.exists(fpath):
            dataset, created = Dataset.objects.get_or_create(
                user=admin_user,
                name=s['name'],
                defaults={'description': s['desc'], 'file_format': 'CSV', 'is_favorite': True}
            )
            if created:
                with open(fpath, 'rb') as f:
                    version = DatasetVersion.objects.create(
                        dataset=dataset,
                        version_number=1,
                    )
                    version.file.save(s['file'], ContentFile(f.read()))
                    meta = analyze_dataset_metadata(version.file.path)
                    version.row_count = meta['row_count']
                    version.column_count = meta['column_count']
                    version.memory_usage_bytes = meta['memory_usage_bytes']
                    version.memory_usage_str = meta['memory_usage_str']
                    version.duplicate_rows = meta['duplicate_rows']
                    version.missing_values = meta['missing_values']
                    version.numerical_cols = meta['numerical_cols']
                    version.categorical_cols = meta['categorical_cols']
                    version.save()
                    print(f"Seeded Dataset: {dataset.name} (v1)")

                # Create sample Trained Models for the dataset
                if s['file'] == 'car_data.csv':
                    TrainedModel.objects.get_or_create(
                        user=admin_user,
                        dataset=dataset,
                        name="Random Forest Regressor (Car Sales)",
                        model_type="REGRESSION",
                        algorithm="Random Forest",
                        target_column="Selling_Price",
                        feature_columns=["Year", "Present_Price", "Kms_Driven", "Owner"],
                        metrics={"r2_score": 0.942, "mae": 0.85, "mse": 1.42, "rmse": 1.19, "accuracy": 0.942},
                        accuracy=0.942,
                        is_public=True
                    )
                    TrainedModel.objects.get_or_create(
                        user=admin_user,
                        dataset=dataset,
                        name="Multiple Linear Regression (Car Sales)",
                        model_type="REGRESSION",
                        algorithm="Linear Regression",
                        target_column="Selling_Price",
                        feature_columns=["Year", "Present_Price", "Kms_Driven"],
                        metrics={"r2_score": 0.885, "mae": 1.12, "mse": 2.10, "rmse": 1.44, "accuracy": 0.885},
                        accuracy=0.885,
                        is_public=True
                    )
                elif s['file'] == 'students.csv':
                    TrainedModel.objects.get_or_create(
                        user=admin_user,
                        dataset=dataset,
                        name="Decision Tree Classifier (Students)",
                        model_type="CLASSIFICATION",
                        algorithm="Decision Tree (Entropy)",
                        target_column="Result",
                        feature_columns=["Age", "Study_Hours", "Attendance_Pct", "Prev_Score"],
                        metrics={"accuracy": 0.933, "error_rate": 0.067, "sensitivity": 0.95, "specificity": 0.92, "precision": 0.94, "recall": 0.95, "f1_score": 0.945},
                        accuracy=0.933,
                        is_public=True
                    )

    print("IntelliHub AI Database Seeding Complete!")

if __name__ == '__main__':
    run_seed()
