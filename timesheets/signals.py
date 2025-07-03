from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import Timesheet, Day


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
