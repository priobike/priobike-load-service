from datetime import datetime, timedelta

from app.models import Bucket
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Store in the database when the service was started. """

    def handle(self, *args, **options):
        # Create random cpms for the last 5 weeks
        start_time = datetime.now()
        bucket_length = timedelta(seconds=60)
        for i in range(5 * 7 * 24 * 60):
            end_time = start_time - bucket_length
            cpm = i % 100
            Bucket.objects.create(start_time=start_time, end_time=end_time, cpm=cpm)
            start_time = end_time

            if i % 1000 == 0:
                print(f"Created {i} buckets out of {5 * 7 * 24 * 60}.")
        
        print(f"Created {5 * 7 * 24 * 60} buckets.")
