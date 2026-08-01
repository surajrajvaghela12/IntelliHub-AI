from django.test import TestCase
import pandas as pd
import numpy as np
import os

from apps.ml_studio.services import train_regression_model, train_classification_model

class MLStudioTestCase(TestCase):
    def setUp(self):
        self.test_csv_path = "media/samples/car_data.csv"

    def test_regression_training(self):
        if os.path.exists(self.test_csv_path):
            model, metrics, features = train_regression_model(
                self.test_csv_path,
                target_col="Selling_Price",
                feature_cols=["Year", "Present_Price", "Kms_Driven"],
                algorithm="multiple_linear"
            )
            self.assertIn("r2_score", metrics)
            self.assertIn("mae", metrics)
            self.assertIn("mse", metrics)
            self.assertIn("rmse", metrics)

    def test_classification_training(self):
        student_csv = "media/samples/students.csv"
        if os.path.exists(student_csv):
            model, metrics, features = train_classification_model(
                student_csv,
                target_col="Result",
                feature_cols=["Age", "Study_Hours", "Attendance_Pct", "Prev_Score"],
                algorithm="decision_tree"
            )
            self.assertIn("accuracy", metrics)
            self.assertIn("confusion_matrix", metrics)
            self.assertIn("sensitivity", metrics)
            self.assertIn("specificity", metrics)

    def test_automl_execution(self):
        if os.path.exists(self.test_csv_path):
            from apps.ml_studio.services import run_automl
            candidates = run_automl(self.test_csv_path, target_col="Selling_Price", task_type="regression")
            self.assertGreater(len(candidates), 0)
