import json
import pytz
from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from app.models import Start

PAST_WEEKS = 3
BUCKET_SIZE = timedelta(minutes=30)

class Command(BaseCommand):
    help = """ Estimates the current load (based on the past week(s)). """
    
    def handle(self, *args, **kwargs):
        current_bucket_end = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
        current_bucket_begin = current_bucket_end - BUCKET_SIZE
        
        current_bucket_start_counts = Start.objects.filter(time__gte=current_bucket_begin, time__lte=current_bucket_end).count()    
        
        past_buckets = [0 for _ in range(PAST_WEEKS)]
        
        for i in range(PAST_WEEKS):
            diff = i + 1
            start_count = Start.objects.filter(time__gte=current_bucket_begin - timedelta(weeks=diff), time__lte=current_bucket_end - timedelta(weeks=diff)).count()
            past_buckets[i] = start_count
            
        past_buckets_avg = sum(past_buckets) / len(past_buckets)
        
        warning = False
        
        if past_buckets_avg > 0 and current_bucket_start_counts > past_buckets_avg * 2:
            warning = True
            response_text = "Aktuell verzeichnen wir deutlich mehr Nutzende als in den letzten Wochen. Moin an alle Neulinge!\n" + \
                            "Sollte es dadurch jedoch zu Problemen bei den Ladezeiten kommen, bitten wir um Verständnis. Wir arbeiten permanent an der Verbesserung der Performance. " + \
                            "Bei Problemen meldet Euch gerne bei uns."
        
        if warning:
            response_json = {
                "warning": warning,
                "response_text": response_text
            }
        else:
            response_json = {
                "warning": warning
            }
        
        with open(str(settings.BASE_DIR) + f"/static/load_response.json", "w") as f:
            f.write(json.dumps(response_json))
        
            
        
            
        
            
            
        
        