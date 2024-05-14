from django.db import models
from django.utils import timezone


class LoadServiceStartup(models.Model):
    # The time the app was started.
    time = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"Service startup at {self.time}"
