from django.test import TestCase
import pandas as pd
import numpy as np

from apps.eda.services import (
    get_eda_summary_statistics,
    compute_two_way_crosstab,
    generate_networkx_visualization,
    create_plotly_chart
)

class EDAServicesTestCase(TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'Age': [20, 21, 22, 23, 24, 25],
            'Score': [80, 85, 90, 95, 100, 105],
            'Gender': ['M', 'F', 'M', 'F', 'M', 'F']
        })

    def test_networkx_visualization(self):
        graph_json, node_degrees = generate_networkx_visualization(self.df)
        self.assertIn("data", graph_json)
        self.assertIn("layout", graph_json)
        self.assertIn("Age", node_degrees)

    def test_plotly_chart_creation(self):
        chart_json = create_plotly_chart(self.df, 'scatter', x_col='Age', y_col='Score')
        self.assertIn("data", chart_json)
        self.assertIn("layout", chart_json)

    def test_crosstab(self):
        html = compute_two_way_crosstab(self.df, 'Gender', 'Age')
        self.assertIn("table", html)
