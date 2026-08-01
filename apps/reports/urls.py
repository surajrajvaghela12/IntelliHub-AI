from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_center_view, name='home'),
    path('<int:dataset_id>/', views.report_center_view, name='home'),
    path('<int:dataset_id>/download/', views.download_pdf_report_view, name='download'),
]
