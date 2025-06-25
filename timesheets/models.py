from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

# Create your models here.


# Project Model:
class Project(models.Model):
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

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError({
                'end_date': 'End date must be after start date.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()  # Enforces the clean() validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Contributor Model:
class Contributor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=CONTRIBUTOR_STATUS, default='active')

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.username} - {self.project.name}"