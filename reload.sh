#! /bin/bash

echo " Stopping Containers...."

docker compose down

echo " Starting Containers..."
docker compose up -d

echo " Reload Containers Done..."

