from django.urls import path
from . import views

app_name = 'eda'

urlpatterns = [
    path('', views.eda_dashboard_view, name='home'),
    path('<int:dataset_id>/', views.eda_dashboard_view, name='home'),
]
