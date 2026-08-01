from django.urls import path
from . import views

app_name = 'cleaner'

urlpatterns = [
    path('', views.cleaner_home_view, name='home'),
    path('<int:dataset_id>/', views.cleaner_home_view, name='home'),
    path('<int:dataset_id>/auto/', views.trigger_auto_clean_view, name='auto_clean'),
    path('<int:dataset_id>/custom/', views.trigger_custom_clean_view, name='custom_clean'),
]
