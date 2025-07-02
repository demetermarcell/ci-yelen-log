from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Project, Timesheet, Day
from django.db.models import Prefetch 

# Create your views here.
@login_required
def projects_dashboard(request):
    user = request.user
    owned_projects = Project.objects.filter(owner=user)
    assigned_projects = Project.objects.filter(contributors=user)

    context = {
        'owned_projects': owned_projects,
        'assigned_projects': assigned_projects,
    }
    return render(request, 'timesheets/projects_dashboard.html', context)



@login_required
def project_view(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_owner = request.user == project.owner

    # Timesheets by user for this project
    my_timesheets = Timesheet.objects.filter(
        user=request.user, project=project
    ).order_by('-start_date')

    # All project timesheets, only visible to owner
    project_timesheets = Timesheet.objects.filter(
        project=project,
        status__in=['submitted', 'approved', 'rejected']
    ).order_by('-submitted_on') if is_owner else None

    contributors = project.contributors.all() if is_owner else None

    context = {
        'project': project,
        'is_owner': is_owner,
        'contributors': contributors,
        'my_timesheets': my_timesheets,
        'project_timesheets': project_timesheets,
    }
    return render(request, 'timesheets/project_view.html', context)


@login_required
def timesheet_view(request, slug):
    timesheet = get_object_or_404(Timesheet, slug=slug)

    days = Day.objects.filter(timesheet=timesheet).order_by('day_date').prefetch_related('task_entries')

    return render(request, 'timesheets/timesheet_view.html', {
        'timesheet': timesheet,
        'days': days,
    })
