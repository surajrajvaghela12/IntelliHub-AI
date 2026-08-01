from django.urls import path
from . import views

app_name = 'ml_studio'

urlpatterns = [
    path('', views.ml_studio_home_view, name='home'),
    path('<int:dataset_id>/', views.ml_studio_home_view, name='home'),
    path('<int:dataset_id>/automl/', views.trigger_automl_view, name='automl'),
    path('leaderboard/', views.model_leaderboard_view, name='leaderboard'),
    path('marketplace/', views.model_marketplace_view, name='marketplace'),
    path('predict/<int:model_id>/', views.predict_live_view, name='predict'),
]
