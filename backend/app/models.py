from django.conf import settings
from django.db import models
from django.utils import timezone


class Start(models.Model):
    """An app start."""

    # The time the app was started.
    time = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"App start at {self.time}"

    class Meta:
        verbose_name = "App start"
        verbose_name_plural = "App starts"