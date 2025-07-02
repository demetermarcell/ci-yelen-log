from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects_dashboard, name='projects_dashboard'),
    path('project/<slug:slug>/', views.project_view, name='project_view'),
    path('project/<slug:slug>/create-timesheet/', views.create_timesheet, name='create_timesheet'),# Used by the timesheet creation form modal in project_view.html to submit new timesheet data
    path('timesheet/<slug:slug>/edit/', views.timesheet_edit, name='timesheet_edit'),
    path('timesheet/<slug:slug>/', views.timesheet_view, name='timesheet_view'),

]
