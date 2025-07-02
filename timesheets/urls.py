from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects_dashboard, name='projects_dashboard'),
    path('project/<slug:slug>/', views.project_view, name='project_view'),
    path('timesheet/<slug:slug>/', views.timesheet_view, name='timesheet_view'),

]
