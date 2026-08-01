from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('', views.assistant_chat_view, name='chat'),
    path('<int:dataset_id>/', views.assistant_chat_view, name='chat'),
]
