import json
import socket
import time
from datetime import datetime, timedelta

import pytz
import requests
from app.models import Bucket, Status
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models

PAST_WEEKS = 3

class Command(BaseCommand):
    """
    This command is executed by the manager to sync statistics from the workers.
    """
    
    def add_arguments(self, parser):
        parser.add_argument("--host", type=str, help="The host to sync from.")
        parser.add_argument("--port", type=int, help="The port to sync from.")
        parser.add_argument("--interval", type=int, default=60, help="The interval in seconds to sync.")

    def handle(self, *args, **options):
        if not options["host"]:
            raise ValueError("Missing required argument: --host")
        if not options["port"]:
            raise ValueError("Missing required argument: --port")
        if not options["interval"]:
            raise ValueError("Missing required argument: --interval")
        
        host = options["host"]
        port = options["port"]
        interval = options["interval"]

        while True:
            # Get the data from the workers.
            worker_hosts = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
            worker_ips = [worker_host[4][0] for worker_host in worker_hosts]

            current_bucket_end = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
            current_bucket_begin = current_bucket_end - timedelta(seconds=interval)
            
            print(f"Syncing with workers for bucket {current_bucket_begin} - {current_bucket_end}")

            cpms = []

            # Fetch the status for now
            for worker_ip in worker_ips:
                print(f"Syncing with worker: {worker_ip}")
                url = f"http://{worker_ip}:{port}/sync/sync"
                try:
                    response = requests.get(url, params={
                        "key": settings.SYNC_KEY,
                        "start": current_bucket_begin.isoformat(),
                        "end": current_bucket_end.isoformat()
                    })
                except requests.exceptions.ConnectionError:
                    print(f"Worker {worker_ip} seems offline")
                    continue
                if response.status_code != 200:
                    print(f"Failed to sync with worker {worker_ip}: status {response.status_code}")
                    continue
                if not response.text:
                    print(f"Empty response from worker {worker_ip}")
                    continue
                response_json = response.json()
                cpm = response_json["cpm"]
                if cpm is None:
                    print(f"Invalid response from worker {worker_ip}")
                    continue
                print(f"Worker {worker_ip} has detected {cpm} app starts per minute")
                cpms.append(cpm)

            if len(cpms) == 0:
                print("Warning: No workers responded with valid data. Skipping this bucket.")
                time.sleep(interval)
                continue
            cpm = sum(cpms)
            print(f"Total cpm: {cpm} (Average per worker: {cpm / len(cpms)})")

            # Get all buckets inside the window on the same weekday
            window_start = current_bucket_begin - timedelta(minutes=15)
            window_end = current_bucket_end + timedelta(minutes=15)
            days_start, days_end = [], []
            for week_idx in range(1, PAST_WEEKS):
                days_start.append(window_start - timedelta(weeks=week_idx))
                days_end.append(window_end - timedelta(weeks=week_idx))
            print(f"Checking buckets from {days_start[0]} to {days_end[0]}")
            print(f"Within the time frame {window_start.time()} to {window_end.time()}")
            buckets = Bucket.objects \
                .filter(start_time__day__in=[day.day for day in days_start]) \
                .filter(end_time__day__in=[day.day for day in days_end]) \
                .filter(start_time__year__in=[day.year for day in days_start]) \
                .filter(end_time__year__in=[day.year for day in days_end]) \
                .filter(start_time__month__in=[day.month for day in days_start]) \
                .filter(end_time__month__in=[day.month for day in days_end]) \
                .filter(end_time__time__gte=window_start.time()) \
                .filter(start_time__time__lte=window_end.time())
            n_buckets = buckets.count()
            print(f"Found {n_buckets} buckets in the past {PAST_WEEKS} weeks.")
            if n_buckets == 0:
                past_buckets_avg = 0
            else:
                past_buckets_avg = buckets.aggregate(models.Avg('cpm'))['cpm__avg']
            print(f"Average cpm in the past buckets: {past_buckets_avg}")

            Bucket.objects.create(
                start_time=current_bucket_begin,
                end_time=current_bucket_end,
                cpm=cpm
            )

            warning = past_buckets_avg > 0 and cpm > past_buckets_avg * 2
            if warning:
                response_text = "Aktuell verzeichnen wir deutlich mehr Nutzende als in den letzten Wochen. Moin an alle Neulinge!\n" + \
                                "Sollte es dadurch jedoch zu Problemen bei den Ladezeiten kommen, bitten wir um Verständnis. Wir arbeiten permanent an der Verbesserung der Performance. " + \
                                "Bei Problemen meldet Euch gerne bei uns."
            else:
                response_text = None

            est_app_starts = cpm * (current_bucket_end - current_bucket_begin).total_seconds() / 60
            status = Status.objects.create(
                warning=warning,
                response_text=response_text,
                bucket_length=(current_bucket_end - current_bucket_begin).total_seconds(),
                app_starts=est_app_starts,
                past_buckets_avg=past_buckets_avg
            )

            print(f"Status updated: {status.app_starts} app starts in the current bucket, {status.past_buckets_avg} in the past buckets. Warning: {status.warning}")

            # Remove outdated buckets
            outdated_buckets = Bucket.objects.filter(end_time__lt=current_bucket_end - timedelta(weeks=PAST_WEEKS))
            n_outdated_buckets = outdated_buckets.count()
            if n_outdated_buckets > 0:
                print(f"Deleting {n_outdated_buckets} outdated buckets")
                outdated_buckets.delete()
            
            # Tell all workers that the status has been updated
            for worker_ip in worker_ips:
                print(f"Syncing status with worker: {worker_ip}")
                url = f"http://{worker_ip}:{port}/sync/sync"
                try:
                    response = requests.post(url, json={
                        "key": settings.SYNC_KEY,
                        "time": status.time.isoformat(),
                        "warning": status.warning,
                        "responseText": status.response_text,
                        "bucketLength": status.bucket_length,
                        "appStarts": status.app_starts,
                        "pastBucketsAvg": status.past_buckets_avg
                    })
                except requests.exceptions.ConnectionError:
                    print(f"Worker {worker_ip} seems offline")
                    continue
                if response.status_code != 200:
                    print(f"Failed to sync with worker {worker_ip}: status {response.status_code}")
                    continue
                print(f"Worker {worker_ip} has been updated with the status")

            time.sleep(interval)
