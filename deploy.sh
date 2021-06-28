#!/bin/sh
docker push "$DOCKER_USERNAME"/todo-app;
curl -dH -X POST "$AZURE_DEPLOY_WEBHOOK"