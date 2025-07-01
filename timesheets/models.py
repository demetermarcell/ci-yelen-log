from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.db.models import Q
from uuid import uuid4


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
TIMESHEET_STATUS = (
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected')
)

# Day Statuses:
DAY_STATUS = (
    ('working', 'Working Day'),
    ('sick', 'Sick Day'),
    ('off', 'Day Off'),
    ('weekend', 'Weekend')
)

# Task Types:
TASK_TYPE = (
    ('development', 'Development'),
    ('code_review', 'Code Review'),
    ('bug_fixing', 'Bug Fixing'),
    ('testing', 'Testing'),       
    ('internal_meeting', 'Internal Meeting'),
    ('external_meeting', 'External Meeting'),
    ('admin', 'Admin'),
    ('documentation', 'Documentation'),
    ('support', 'Support'),
    ('other', 'Other'),
)

# Create your models here.


# Project Model:
class Project(models.Model):
    # Fields:
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False, blank=True) # Unique slug for encrypted URLs
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

    # Meta options:
    class Meta:
        unique_together = ('name', 'start_date')

    # Validation:
    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError({ 
                'end_date': 'End date must be after start date.'
            })

    # Save Method:
    def save(self, *args, **kwargs):
        # Autogenerate slug, unique per project, for encrypded URLs.
        if not self.slug:
            self.slug = uuid4().hex[:12]
        self.full_clean()  # Enforces the clean() validation before saving
        super().save(*args, **kwargs)

    # String Representation:
    def __str__(self):
        return f"{self.name} ({self.start_date})"


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
    slug = models.SlugField(unique=True, editable=False, blank=True)  # Unique slug for encrypted URLs
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timesheets')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timesheets')
    start_date = models.DateField()
    end_date = models.DateField()
    total_hours_logged = models.FloatField(default=0, editable=False)  # SUM of all task hours
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
        # Skip validation if required fields are missing
        if not self.start_date or not self.end_date or not self.project:
            return
        # Validate the user is an active contributor to the project:
        if not Contributor.objects.filter(
                user=self.user,
                project=self.project,
                status='active'
        ).exists():
            raise ValidationError({'user': "User must be an active contributor to the project."})
        # Validate the project is active:
        if self.project.status != 'active':
            raise ValidationError({'project': "Project must be active to log timesheets."})
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
        # Autogenerate slug, unique per project, for encrypded URLs.
        if not self.slug:
            self.slug = uuid4().hex[:12]
        self.full_clean()
        super().save(*args, **kwargs)

    # Update total hours logged:
    def update_total_hours(self):
        total = self.days.aggregate(models.Sum('total_hours_logged'))['total_hours_logged__sum'] or 0
        self.total_hours_logged = total
        self.save(update_fields=['total_hours_logged'])

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
    total_hours_logged = models.FloatField(default=0, editable=False) 

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

        # Delete tasks if status is changed from 'working' to something else
        if self.pk:
            try:
                old = Day.objects.get(pk=self.pk)
                if old.status == 'working' and self.status != 'working':
                    self.task_entries.all().delete()
                    self.total_hours_logged = 0
            except Day.DoesNotExist:
                pass  # safe fallback if instance is deleted between fetch and save

        super().save(*args, **kwargs)

    # Update total hours logged:
    def update_total_hours(self, cascade=True):
        # Safeguard. Avoid updating if the Day hasn't been saved yet
        if not self.pk:
            return

        total = self.task_entries.aggregate(models.Sum('hours_logged'))['hours_logged__sum'] or 0
        total = min(total, 24)

        if total != self.total_hours_logged:
            self.total_hours_logged = total
            self.save(update_fields=['total_hours_logged'])

            if cascade:
                self.timesheet.update_total_hours()

    # String Representation:
    def __str__(self):
        return f"{self.timesheet.user.username} - {self.day_name} ({self.day_date}) - {self.get_status_display()}"


# Task Model:
class Task(models.Model):
    # Fields:
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='task_entries')
    task_type = models.CharField(max_length=20, choices=TASK_TYPE, default='other')
    hours_logged = models.FloatField()

    # Validation:
    def clean(self):
        # Ensure day status is 'working':
        if self.day.status != 'working':
            raise ValidationError('Tasks can only be logged on working days.')
        #  Ensure hours are within valid range:
        if not (0 <= self.hours_logged <= 24):
            raise ValidationError({
                'hours_logged': 'Hours logged must be between 0 and 24.'
            })
        # Total including this task must not exceed 24
        existing_total = self.day.task_entries.exclude(pk=self.pk).aggregate(
            models.Sum('hours_logged')
        )['hours_logged__sum'] or 0

        if existing_total + self.hours_logged > 24:
            raise ValidationError("Total logged hours for the day cannot exceed 24.")

    # Meta options:
    class Meta:
        unique_together = ('day', 'task_type')  # Prevent duplicate tasks of the same type on the same day
        ordering = ['day__day_date', 'task_type']  # Order by date then task type

    # Save Method:
    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures `clean()` and field validators run before saving
        super().save(*args, **kwargs)
        self.day.update_total_hours()

    # Delete Method:
    # Ensures total hours are updated when a task is deleted
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.day.update_total_hours()

    # String Representation:
    def __str__(self):
        return f"{self.get_task_type_display()} - {self.hours_logged}h on {self.day.day_date}"