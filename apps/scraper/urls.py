from django.urls import path
from . import views

app_name = 'scraper'

urlpatterns = [
    path('', views.scraper_home_view, name='home'),
]
