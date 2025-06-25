from django.contrib import admin
from .models import Project, Contributor
from django_summernote.admin import SummernoteModelAdmin


# Register the Contributor model with the Django admin interface:
@admin.register(Contributor)
class ContributorAdmin(SummernoteModelAdmin):

    list_display = ('user', 'project', 'status')
    search_fields = ['project__name', 'user__username']
    list_filter = ('project', 'user','status',)


# Register the Project model with the Django admin interface:
@admin.register(Project)
class ProjectAdmin(SummernoteModelAdmin):

    list_display = ('name', 'owner', 'start_date', 'end_date', 'status')
    search_fields = ['name', 'owner__username']
    list_filter = ('name', 'owner', 'status',)


# Register your models here.

