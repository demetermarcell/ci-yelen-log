from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Project


# Create your views here.
@login_required
def projects_dashboard(request):
    user = request.user
    owned_projects = Project.objects.filter(owner=user)
    assigned_projects = Project.objects.filter(contributors=user).exclude(owner=user)

    context = {
        'owned_projects': owned_projects,
        'assigned_projects': assigned_projects,
    }
    return render(request, 'timesheets/projects_dashboard.html', context)



@login_required
def project_view(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'timesheets/project_view.html', {'project': project})
