from django.shortcuts import render


# Create your views here.
def project_dashboard(request):
    return render(request, 'timesheets/project_dashboard.html')
