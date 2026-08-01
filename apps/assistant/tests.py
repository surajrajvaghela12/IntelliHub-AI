from django.test import TestCase
import pandas as pd

from apps.assistant.services import ask_ai_data_analyst

class AssistantTestCase(TestCase):
    def test_highest_correlation_query(self):
        res = ask_ai_data_analyst("Which column has the highest correlation?")
        self.assertIn("Correlation", res)
