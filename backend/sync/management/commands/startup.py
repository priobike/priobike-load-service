from django.core.management.base import BaseCommand
from sync.models import LoadServiceStartup


class Command(BaseCommand):
    """ Store in the database when the service was started. """

    def handle(self, *args, **options):
        LoadServiceStartup.objects.create()
