from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Project, Timesheet, Day, Contributor
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from django.core.exceptions import ValidationError


# Create your views here.
# Projects Dashboard View
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


# Project View:
@login_required
def project_view(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_owner = request.user == project.owner

    # Check if the user is an active contributor to the project
    is_contributor = Contributor.objects.filter(
        user=request.user,
        project=project,
        status='active'
    ).exists()

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

    # Calculate default start and end dates for new timesheet:
    latest_ts = my_timesheets.first()
    if latest_ts:
        default_start = latest_ts.end_date + timedelta(days=1)
    else:
        default_start = max(project.start_date, timezone.now().date())

    default_end = default_start + timedelta(days=6)

    context = {
        'project': project,
        'is_owner': is_owner,
        'is_contributor': is_contributor,
        'contributors': contributors,
        'my_timesheets': my_timesheets,
        'project_timesheets': project_timesheets,
        'default_start': default_start,
        'default_end': default_end,
    }
    return render(request, 'timesheets/project_view.html', context)


# Timesheet View:
@login_required
def timesheet_view(request, slug):
    timesheet = get_object_or_404(Timesheet, slug=slug)

    project = timesheet.project
    user = request.user
    is_owner = user == project.owner
    # Approve/Reject logic only for owners:
    if request.method == "POST" and is_owner and timesheet.status == "submitted":
        action = request.POST.get("action")
        if action == "approve":
            timesheet.status = "approved"
            timesheet.approved_on = timezone.now()
            timesheet.save()
            messages.success(request, "Timesheet approved.")
        elif action == "reject":
            timesheet.status = "rejected"
            timesheet.save()
            messages.warning(request, "Timesheet rejected.")
        return HttpResponseRedirect(reverse('timesheet_view', args=[timesheet.slug]))

    days = timesheet.days.prefetch_related('task_entries').order_by('day_date')

    return render(request, 'timesheets/timesheet_view.html', {
        'timesheet': timesheet,
        'days': days,
        'is_owner': is_owner,
    })


# Create Timesheet View:
@login_required
def create_timesheet(request, slug):
    project = get_object_or_404(Project, slug=slug)
    
    # Check contributor access
    if not Contributor.objects.filter(user=request.user, project=project, status='active').exists():
        messages.error(request, "You are not an active contributor to this project.")
        return HttpResponseRedirect(reverse('project_view', args=[slug]))

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Convert and validate dates
        try:
            start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return HttpResponseRedirect(reverse('project_view', args=[slug]))

        # Create instance
        timesheet = Timesheet(user=request.user, project=project, start_date=start_date, end_date=end_date)

        try:
            timesheet.save()
            messages.success(request, "Timesheet created.")
            # Redirect to edit view:
            return HttpResponseRedirect(reverse('timesheet_edit', args=[timesheet.slug]))
        # Remove __all__ from Validation Error messages:
        except ValidationError as e:
            errors = []
            for field, msgs in e.message_dict.items():
                if field == '__all__':
                    errors.extend(msgs)  # Don't prepend field name
                else:
                    errors.extend([f"{field}: {msg}" for msg in msgs])
            messages.error(request, " ".join(errors))
            return HttpResponseRedirect(reverse('project_view', args=[slug]))

# Edit Timesheet:
@login_required
def timesheet_edit(request, slug):
    timesheet = get_object_or_404(Timesheet, slug=slug)

    if request.user != timesheet.user:
        messages.error(request, "You are not authorized to edit this timesheet.")
        return HttpResponseRedirect(reverse('project_view', args=[timesheet.project.slug]))

    return render(request, 'timesheets/timesheet_edit.html', {
        'timesheet': timesheet,
    })