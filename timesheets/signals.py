from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import timedelta
from django.db.models import Sum
from .models import Timesheet, Day, Task


# Signals to automatically generate Day instances for a Timesheet
@receiver(post_save, sender=Timesheet)
def generate_days_for_timesheet(sender, instance, created, **kwargs):
    if created and not instance.days.exists():
        # Calculate number of days between start and end
        day_count = (instance.end_date - instance.start_date).days + 1
        for i in range(day_count):
            day_date = instance.start_date + timedelta(days=i)
            Day.objects.create(
                timesheet=instance,
                day_date=day_date,
            )


# Signal to update total hours logged in a Timesheet when Tasks are created or deleted
# def update_timesheet_total(timesheet):
#     total = Task.objects.filter(day__timesheet=timesheet).aggregate(
#         total=Sum('hours_logged')
#     )['total'] or 0
#     timesheet.total_hours_logged = total
#     timesheet.save(update_fields=['total_hours_logged'])

# @receiver(post_save, sender=Task)
# @receiver(post_delete, sender=Task)
# def sync_timesheet_hours(sender, instance, **kwargs):
#     update_timesheet_total(instance.day.timesheet)
