from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.db.models import Q

# CHOICES

# Project Statuses:
PROJECT_STATUS = (
    ('active', 'Active'),
    ('on_hold', 'On Hold'),
    ('closed', 'Closed'),
)

# Contributor Statuses:
CONTRIBUTOR_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)

# Timesheet Statuses:
TIMESHEET_STATUS = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected')
]

# Day Statuses:
DAY_STATUS = [
    ('working', 'Working Day'),
    ('sick', 'Sick Day'),
    ('off', 'Day Off'),
    ('weekend', 'Weekend')
]
# Create your models here.


# Project Model:
class Project(models.Model):
    # Fields:
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='active')
    contributors = models.ManyToManyField(
        User,
        through='Contributor',
        related_name='contributed_projects'
    )

    # Validation:
    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError({ 
                'end_date': 'End date must be after start date.'
            })

    # Save Method:
    def save(self, *args, **kwargs):
        self.full_clean()  # Enforces the clean() validation before saving
        super().save(*args, **kwargs)

    # String Representation:
    def __str__(self):
        return self.name


# Contributor Model:
class Contributor(models.Model):
    # Fields:
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=CONTRIBUTOR_STATUS, default='active')

    # Meta options:
    class Meta:
        unique_together = ('user', 'project')

    # String Representation:
    def __str__(self):
        return f"{self.user.username} - {self.project.name}"


# Timesheet Model:
class Timesheet(models.Model):
    # Fields:
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timesheets')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timesheets')
    start_date = models.DateField()
    end_date = models.DateField()
    total_hours_logged = models.FloatField(default=0)  # SUM of all task hours
    status = models.CharField(
        max_length=20,
        choices=TIMESHEET_STATUS,
        default='draft'
    )
    submitted_on = models.DateTimeField(null=True, blank=True)
    approved_on = models.DateTimeField(null=True, blank=True)

    # Meta options:
    class Meta:
        unique_together = ('user', 'project', 'start_date')  # avoid duplicate entries per user/project/week
        ordering = ['-start_date', 'user']  # most recent timesheets first

    # Validation:
    def clean(self):
        if not self.project or not self.start_date or not self.end_date:
            return
        # Validate start date is before end date:
        if self.start_date > self.end_date:
            raise ValidationError({'end_date': "End date must be after start date."})
        # Validate full range is inside project period
        project_end = self.project.end_date or self.start_date
        if not (self.project.start_date <= self.start_date <= project_end):
            raise ValidationError({'start_date': "Timesheet start date must be within the project's active dates."})
        if not (self.project.start_date <= self.end_date <= project_end):
            raise ValidationError({'end_date': "Timesheet end date must be within the project's active dates."})
        # Ensure no overlapping timesheets for the same user/project.
        overlapping_timesheets = Timesheet.objects.filter(
            user=self.user,
            project=self.project,
        ).exclude(pk=self.pk).filter(  # Exclude current instance from check
            Q(start_date__lte=self.end_date) &  # Check if start date is before or equal to end date
            Q(end_date__gte=self.start_date)  # Check if end date is after or equal to start date
        )
        if overlapping_timesheets.exists():
            raise ValidationError("This timesheet overlaps with an existing one for the same user and project.")

    # Save Method:
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # String Representation:
    def __str__(self):
        return f"Timesheet of {self.user.username} for {self.project.name} for the week of {self.start_date} - ({self.status})"


# Day Model:
class Day(models.Model):
    # Fields:
    timesheet = models.ForeignKey('Timesheet', on_delete=models.CASCADE, related_name='days')
    day_date = models.DateField()
    status = models.CharField(max_length=10, choices=DAY_STATUS)
    comments = models.TextField(blank=True)
    day_name = models.CharField(max_length=10, editable=False)

    # Meta options:
    class Meta:
        unique_together = ('timesheet', 'day_date')  # Ensure no duplicate days in a timesheet

    # Save Method:
    def save(self, *args, **kwargs):
        # Set day_name from date
        self.day_name = self.day_date.strftime("%A")  # e.g., 'Monday'

        # Auto-assign default status if not manually set
        if not self.status:
            if self.day_name in ['Saturday', 'Sunday']:
                self.status = 'weekend'
            else:
                self.status = 'working'

        super().save(*args, **kwargs)

    # String Representation:
    def __str__(self):
        return f"{self.day_name} ({self.day_date}) - {self.get_status_display()}"
