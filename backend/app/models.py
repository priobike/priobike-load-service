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


class Bucket(models.Model):
    # The start time of the bucket.
    start_time = models.DateTimeField()

    # The end time of the bucket.
    end_time = models.DateTimeField()

    # The total number of clicks per minute in the bucket.
    cpm = models.IntegerField(default=0)


class Status(models.Model):
    # The time the status was last updated.
    time = models.DateTimeField(default=timezone.now)

    # Whether a warning should be displayed.
    warning = models.BooleanField(default=False)

    # The response text to display.
    response_text = models.TextField(blank=True, null=True)

    # The bucket length in seconds.
    bucket_length = models.IntegerField(default=1800)

    # The number of app starts registered in the current bucket.
    app_starts = models.IntegerField(default=0)

    # The average number of app starts in the past buckets.
    past_buckets_avg = models.FloatField(default=0)

    def __str__(self) -> str:
        return f"Status at {self.time}: {self.response_text}"
