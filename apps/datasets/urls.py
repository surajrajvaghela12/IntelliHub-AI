from django.urls import path
from . import views

app_name = 'datasets'

urlpatterns = [
    path('', views.dataset_list_view, name='list'),
    path('upload/', views.dataset_upload_view, name='upload'),
    path('<int:dataset_id>/', views.dataset_detail_view, name='detail'),
    path('<int:dataset_id>/version/', views.dataset_new_version_view, name='upload_version'),
    path('<int:dataset_id>/favorite/', views.dataset_toggle_fav_view, name='toggle_fav'),
    path('<int:dataset_id>/delete/', views.dataset_delete_view, name='delete'),
    path('<int:dataset_id>/download/', views.dataset_download_view, name='download'),
]
