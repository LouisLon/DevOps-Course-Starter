#!/bin/sh
set -e
docker push "$DOCKER_USERNAME"/todo-app;
curl -dH -X POST "$AZURE_DEPLOY_WEBHOOK"