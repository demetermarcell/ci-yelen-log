from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import (
    Project,
    Contributor,
    Timesheet,
    Day,
    Task,
)


# Contributor Admin
@admin.register(Contributor)
class ContributorAdmin(SummernoteModelAdmin):
    list_display = ('user', 'project', 'status')
    search_fields = ['project__name', 'user__username']
    list_filter = ('project', 'user', 'status')


# Project Admin
@admin.register(Project)
class ProjectAdmin(SummernoteModelAdmin):
    list_display = ('name', 'owner', 'start_date', 'end_date', 'status')
    search_fields = ['name', 'owner__username']
    list_filter = ('name', 'owner', 'status')
    readonly_fields = ('slug',)


# Timesheet Admin
@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'project', 'start_date', 'end_date',
        'status', 'total_hours_logged', 'slug'
    )
    search_fields = ['user__username', 'project__name']
    list_filter = ('status', 'project', 'user', 'start_date')
    readonly_fields = ('slug', 'total_hours_logged', 'submitted_on', 'approved_on')


# Day Admin
@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = (
        'timesheet', 'day_date', 'day_name',
        'status', 'total_hours_logged'
    )
    search_fields = ['timesheet__user__username', 'timesheet__project__name']
    list_filter = ('status', 'day_name', 'day_date')
    readonly_fields = ('day_name', 'total_hours_logged')


# Task Admin
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('day', 'task_type', 'hours_logged')
    search_fields = [
        'day__timesheet__user__username',
        'day__timesheet__project__name'
    ]
    list_filter = ('task_type', 'day__day_date')
