#!/usr/bin/env bash
echo "Running deployment script...push image to docker"
docker push "$DOCKER_USERNAME"/todo-app;
echo "Running deployment script...Azure docker pull request"
curl -dH -X POST "$AZURE_DEPLOY_WEBHOOK"
echo "Pushed deployment successfully"
exit 0