# priobike-load-service

A small service that fetches the current load metrics from each physical node and estimates the overall load in the deployment. 

This service is based on the node exporter setup in https://github.com/priobike/priobike-prometheus/tree/main which adds metadata about the hosting physical node to the exported metrics.

In PrioBike, this service is used by the app to monitor and trigger the failover to our secondary deployment, in case the primary deployment exceeds its capacity.

[Learn more about PrioBike](https://github.com/priobike)

## Quickstart

```
docker-compose up
```

## API

#### GET `/load.json`

Example response

```json
{
  "timestamp": 1720523821,
  "recommendOtherBackend": false,
  "warning": false
}
```

`recommendOtherBackend`: whether the failover to the secondary backend should be triggered.
`warning`: whether a warning should be displayed in the app, notifying users of increased load.


## What else to know

This service can run in two modes: manager and worker. The worker mode is designed to face user traffic and can be scaled horizontally. Messages are synced between the worker and manager containers. See `docker-compose.yml` for an example setup.

## Contributing

We highly encourage you to open an issue or a pull request. You can also use our repository freely with the `MIT` license. 

Every service runs through testing before it is deployed in our release setup. Read more in our [PrioBike deployment readme](https://github.com/priobike/.github/blob/main/wiki/deployment.md) to understand how specific branches/tags are deployed.

## Anything unclear?

Help us improve this documentation. If you have any problems or unclarities, feel free to open an issue.
