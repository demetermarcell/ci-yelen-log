from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .models import (
    Project,
    Timesheet,
    Contributor,
    DAY_STATUS,
    TASK_TYPE,
)


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


# Project View
@login_required
def project_view(request, slug):
    project = get_object_or_404(Project, slug=slug)
    is_owner = request.user == project.owner

    is_contributor = Contributor.objects.filter(
        user=request.user,
        project=project,
        status='active'
    ).exists()

    my_timesheets = Timesheet.objects.filter(
        user=request.user,
        project=project
    ).order_by('-start_date')

    project_timesheets = (
        Timesheet.objects.filter(
            project=project,
            status__in=['submitted', 'approved', 'rejected']
        ).order_by('-submitted_on')
        if is_owner else None
    )

    contributors = project.contributors.all() if is_owner else None

    latest_ts = my_timesheets.first()
    default_start = (
        latest_ts.end_date + timedelta(days=1)
        if latest_ts else max(project.start_date, timezone.now().date())
    )
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


# Timesheet View
@login_required
def timesheet_view(request, slug):
    timesheet = get_object_or_404(Timesheet, slug=slug)
    project = timesheet.project
    user = request.user
    is_owner = user == project.owner
    is_author = user == timesheet.user

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approve" and is_owner and timesheet.status == "submitted":
            timesheet.status = "approved"
            timesheet.approved_on = timezone.now()
            timesheet.save()
            messages.success(request, "Timesheet approved.")
            return HttpResponseRedirect(reverse('timesheet_view', args=[timesheet.slug]))

        elif action == "reject" and is_owner and timesheet.status == "submitted":
            timesheet.status = "rejected"
            timesheet.save()
            messages.warning(request, "Timesheet rejected.")
            return HttpResponseRedirect(reverse('timesheet_view', args=[timesheet.slug]))

        elif action == "reopen" and is_author and timesheet.status == "rejected":
            timesheet.status = "draft"
            timesheet.submitted_on = None
            timesheet.save()
            messages.info(request, "Timesheet reopened for editing.")
            return HttpResponseRedirect(reverse('timesheet_edit', args=[timesheet.slug]))

    days = timesheet.days.prefetch_related('task_entries').order_by('day_date')  # type: ignore[attr-defined]

    return render(request, 'timesheets/timesheet_view.html', {
        'timesheet': timesheet,
        'days': days,
        'is_owner': is_owner,
    })


# Create Timesheet View
@login_required
def create_timesheet(request: HttpRequest, slug: str) -> HttpResponse | HttpResponseRedirect:
    project = get_object_or_404(Project, slug=slug)

    if not Contributor.objects.filter(user=request.user, project=project, status='active').exists():
        messages.error(request, "You are not an active contributor to this project.")
        return HttpResponseRedirect(reverse('project_view', args=[slug]))

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if not start_date_str or not end_date_str:
            messages.error(request, "Start and end dates are required.")
            return HttpResponseRedirect(reverse('project_view', args=[slug]))

        try:
            start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return HttpResponseRedirect(reverse('project_view', args=[slug]))

        timesheet = Timesheet(
            user=request.user,
            project=project,
            start_date=start_date,
            end_date=end_date
        )

        try:
            timesheet.save()
            messages.success(request, "Timesheet created.")
            return HttpResponseRedirect(reverse('timesheet_edit', args=[timesheet.slug]))
        except ValidationError as e:
            errors = []
            for field, msgs in e.message_dict.items():
                errors.extend(msgs)
            messages.error(request, " ".join(errors))
            return HttpResponseRedirect(reverse('project_view', args=[slug]))

    # Fallback for non-POST requests
    return HttpResponseRedirect(reverse('project_view', args=[slug]))


# Edit Timesheet View
@login_required
def timesheet_edit(request, slug):
    timesheet = get_object_or_404(Timesheet, slug=slug)

    if request.user != timesheet.user:
        messages.error(request, "You are not authorized to edit this timesheet.")
        return HttpResponseRedirect(reverse('project_view', args=[timesheet.project.slug]))

    if request.method == 'POST':
        action = request.POST.get('action')
        errors = []

        for day in timesheet.days.all():  # type: ignore[attr-defined]
            status = request.POST.get(f'status_{day.id}')
            comment = request.POST.get(f'comment_{day.id}')
            day.status = status
            day.comments = comment
            day.task_entries.all().delete()

            if status == 'working':
                for i in range(1, 11):
                    task_type = request.POST.get(f'task_type_{day.id}_{i}')
                    hours = request.POST.get(f'hours_{day.id}_{i}')
                    if task_type and hours:
                        try:
                            day.task_entries.create(
                                task_type=task_type,
                                hours_logged=float(hours)
                            )
                        except ValidationError as e:
                            errors.extend(e.messages)

            try:
                day.save()
            except ValidationError as e:
                errors.extend(e.messages)

        if errors:
            messages.error(request, " ".join(errors))
            return render(request, 'timesheets/timesheet_edit.html', {
                'timesheet': timesheet,
                'day_status_choices': DAY_STATUS,
                'task_type_choices': TASK_TYPE,
            })

        if action == 'submit':
            timesheet.status = 'submitted'
            timesheet.submitted_on = timezone.now()
            messages.success(request, "Timesheet submitted successfully.")
        else:
            timesheet.status = 'draft'
            messages.info(request, "Draft saved.")

        timesheet.save()
        timesheet.update_total_hours()

        return HttpResponseRedirect(reverse('project_view', args=[timesheet.project.slug]))

    return render(request, 'timesheets/timesheet_edit.html', {
        'timesheet': timesheet,
        'day_status_choices': DAY_STATUS,
        'task_type_choices': TASK_TYPE,
    })
