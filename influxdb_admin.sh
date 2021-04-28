#!/bin/bash

echo "Launch InfluxDB as admin"
PASSWORD="$(grep INFLUXDB_ADMIN_PASSWORD env.influxdb | awk -F '=' '{print $2}')"
docker exec -it influxdb influx -username admin -password $PASSWORD