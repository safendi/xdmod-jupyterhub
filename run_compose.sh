#!/bin/bash

echo "Setting up xdmod..."
docker exec -w /root/xdmod xdmod-jupyterhub-webserver-1 composer install
docker exec -w /root/xdmod xdmod-jupyterhub-webserver-1 /root/bin/buildrpm xdmod
docker exec -w /root/xdmod xdmod-jupyterhub-webserver-1 /root/xdmod/tests/ci/bootstrap.sh
