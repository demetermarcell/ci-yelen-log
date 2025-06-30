from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects_dashboard, name='projects_dashboard'),
    path('project/<int:pk>/', views.project_view, name='project_view'),
]
