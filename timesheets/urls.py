from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_dashboard, name='project_dashboard'),
]
