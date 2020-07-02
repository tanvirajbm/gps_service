#!/bin/bash

docker build -t gps_service .

ioxclient docker package -n gps_service gps_service:latest package/