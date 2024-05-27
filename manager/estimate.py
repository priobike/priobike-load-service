import json
import os
import random
import socket
import time
from datetime import datetime

import requests


def log(message):
    """
    Log a message with a timestamp.
    """
    print(f'[{datetime.now()}] {message}', flush=True)


def load_required(key):
    """
    Load a required environment variable.
    """
    value = os.environ.get(key)
    if not value:
        raise ValueError(f'Please provide {key} in the environment')
    return value

# Get the basic auth credentials from the environment
username = os.environ.get('PROMETHEUS_BASIC_AUTH_USERNAME')
password = os.environ.get('PROMETHEUS_BASIC_AUTH_PASSWORD')
prometheus_url = load_required('PROMETHEUS_URL')
# Get the node names from the environment
ingress_node_names = load_required('INGRESS_NODE_NAMES').split(',')
worker_node_names = load_required('WORKER_NODE_NAMES').split(',')
stateful_node_names = load_required('STATEFUL_NODE_NAMES').split(',')
# Get the worker info
worker_username = load_required('WORKER_BASIC_AUTH_USER')
worker_password = load_required('WORKER_BASIC_AUTH_PASS')
worker_host = load_required('WORKER_HOST')
worker_port = load_required('WORKER_PORT')


def push_to_workers(file_path):
    """
    Push a file to all workers.
    """
    with open(file_path) as f:
        file_content = f.read()
    for worker_addr_info in socket.getaddrinfo(worker_host, worker_port, proto=socket.IPPROTO_TCP):
        worker_ip = worker_addr_info[4][0]
        url = f'http://{worker_ip}:{worker_port}/upload/{file_path}'
        retries = 2
        success = False
        while retries > 0:
            response = requests.put(
                url, 
                data=file_content, 
                auth=(worker_username, worker_password),
                headers={'Content-Type': 'application/json'},
            )
            if response.status_code >= 200 and response.status_code < 300:
                success = True
                log(f'Successfully pushed to worker {worker_ip}')
                break
            log(f'Failed to push to worker {worker_ip}, response: {response.text}')
            random_wait_time = random.randint(1, 5)
            log(f"Retrying in {random_wait_time} seconds...")
            time.sleep(random_wait_time)
            retries -= 1
        if not success:
            raise Exception(f'Failed to push to worker {worker_ip}')


def evaluate_cpu_usage():
    """
    Fetch the current CPU usage generated by the node exporter from all nodes.

    See: https://github.com/priobike/priobike-prometheus
    """

    query = '(1 - avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[10m]))) * 100 * on(instance) group_left(node_id, node_name) node_meta'
    url = f'{prometheus_url}/api/v1/query_range'
    end_unix = int(time.time())
    start_unix = end_unix - 60 * 10 # 10 minutes ago
    
    params = {
        'query': query,
        'start': start_unix,
        'end': end_unix,
        'step': 60
    }
    log(f'[INFO] Getting data from {url} with params {params}')
    response = requests.get(url, params=params, auth=(username, password) if username and password else None)
    data = response.json()
    
    if 'data' not in data or 'result' not in data['data']:
        log('[WARN] No data found')
        return
    
    def eval(data, node_name):
        for result in data['data']['result']:
            result_node_name = result['metric']['node_name']
            if result_node_name != node_name:
                continue
            cpu_usages = result['values']
            avg_cpu_usage = sum([float(x[1]) for x in cpu_usages]) / len(cpu_usages) if len(cpu_usages) > 0 else 0
            log(f'[INFO] CPU usage for {node_name}: {avg_cpu_usage:.1f}%')
            return avg_cpu_usage
        log(f'[WARN] No data found for {node_name}')
        return 0

    load_json = { 
        'timestamp': int(time.time()),
        'ingress': sum([eval(data, name) for name in ingress_node_names]) / len(ingress_node_names),
        'worker': sum([eval(data, name) for name in worker_node_names]) / len(worker_node_names),
        'stateful': sum([eval(data, name) for name in stateful_node_names]) / len(stateful_node_names),
    }

    with open("load.json", "w") as outfile:
        json.dump(load_json, outfile, indent=4)

    push_to_workers("load.json")


if __name__ == '__main__':
    evaluate_cpu_usage()