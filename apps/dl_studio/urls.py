from django.urls import path
from . import views

app_name = 'dl_studio'

urlpatterns = [
    path('', views.dl_studio_home_view, name='home'),
]
