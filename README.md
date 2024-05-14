# Load Service

A microservice that estimates the current load on the backend.

## Quickstart

```
docker-compose up
```

## REST Endpoints

#### POST /app/start

```bash
curl -X POST http://localhost/app/start
```

#### GET /monitoring/metrics

```bash
curl "http://localhost:8000/monitoring/metrics?api_key=secret"
```
