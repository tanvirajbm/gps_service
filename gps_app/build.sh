#!/bin/bash

docker build -t gps_client_app .

ioxclient docker package -n gps_client_app gps_client_app:latest package/
