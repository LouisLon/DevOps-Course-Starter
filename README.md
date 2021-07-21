# DevOps Apprenticeship: Project Exercise

## System Requirements

The project uses poetry for Python to create an isolated environment and manage package dependencies. To prepare your system, ensure you have an official distribution of Python version 3.7+ and install poetry using one of the following commands (as instructed by the [poetry documentation](https://python-poetry.org/docs/#system-requirements)):

### Poetry installation (Bash)

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

### Poetry installation (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python
```

## Dependencies

The project uses a virtual environment to isolate package dependencies. To create the virtual environment and install required packages, run the following from your preferred shell:

```bash
$ poetry install
```

You'll also need to clone a new `.env` file from the `.env.tempalate` to store local configuration options. This is a one-time operation on first setup:

```bash
$ cp .env.template .env  # (first time only)
```

The `.env` file is used by flask to set environment variables when running `flask run`. This enables things like development mode (which also enables features like hot reloading when you make a file change). There's also a [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY) variable which is used to encrypt the flask session cookie.

## Running the App

Once the all dependencies have been installed, start the Flask app in development mode within the poetry environment by running:
```bash
$ poetry run flask run
```

You should see output similar to the following:
```bash
 * Serving Flask app "app" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with fsevents reloader
 * Debugger is active!
 * Debugger PIN: 226-556-590
```
Now visit [`http://localhost:5000/`](http://localhost:5000/) in your web browser to view the app.

Notes
The .env file is used by flask to set environment variables when running flask run. This enables things like developement mode (which also enables features like hot reloading when you make a file change).

There's also a SECRET_KEY variable which is used to encrypt the flask session cookie.
The application requires a trello secret key and token for the variables [TRELLO_KEY] [TRELLO_TOKEN] When running setup.sh, the .env.template file will be copied to .env if the latter does not exist.

## Running the Test
The file app_test.py and app_e2e_test.py has the unit test and integration test code
This can be run with test explorer or pytest

You can install pytest via pip
To run pytest, simply run the following command from the root of your project.
```bash
$ pytest
```
## Docker
To build the docker image, run either the `development` or the `production` build
```bash
$ docker build --target development --tag todo-app:dev .
```
```bash
$ docker build --target production --tag todo-app:prod .
```

To run the docker to create a `development` or `production` container from the image
```bash
$ docker run --env-file ./.env -p 5000:5000 --mount type=bind,source="$(pwd)"/todo_app,target=/app/todo_app todo-app:dev
```
For production, the trello key and token is required in the command below
```bash
$ docker run --env TRELLO_KEY=[TRELLO_KEY] --env TRELLO_TOKEN=[TRELLO_TOKEN] --env TRELLO_BOARD_ID=[TRELLO_BOARD_ID] -d -p 127.0.0.1:5000:5000 todo-app:prod
```
## Docker Test Command
To build the docker image, run the `test` build command
```bash
$ docker build --target test --tag todo-app:test .
```
To run
```bash
docker run --mount type=bind,source="$(pwd)"/todo_app,target=/app/todo_app todo-app:test  todo_app/tests/

# E2E test
docker run --env-file ./.env -p 5000:5000 --mount type=bind,source="$(pwd)"/todo_app,target=/app/todo_app todo-app:test todo_app/tests_e2e/
```
## To View the technical UML diagram
load the file documentation\ToDo_UML.drawio file using the site https://app.diagrams.net/

## Automatic Build and deploy to Heroku usint CI Travis
https://travis-ci.com/github/LouisLon/DevOps-Course-Starter
Build docker test image and run tests with the .travis.yml steps
Build docker prod image and deploy to Heroku - https://trelloappex8.herokuapp.com/

This can be deployed manually by the commands
```bash
$ docker build --target production --tag todo-app:prod .
$ docker tag todo-app:prod louiseg/todo-app:latest
$ docker push louiseg/todo-app

$ heroku login
$ heroku container:login
$ docker pull louiseg/todo-app:latest
$ docker tag louiseg/todo-app:latest registry.heroku.com/mongoappex10/web
$ docker push registry.heroku.com/mongoappex10/web
$ heroku container:release web -a mongoappex10 
```
## migration from Trello API to the use MongoDB
Create environment variables
```
[MONGO_USERNAME]
[MONGO_PASSWORD]
[MONGO_DB]
[MONGO_URL]
```
for the MongoDb connection in the .env file or system environment variables
These parameter should be included for Heroku and Travis-CI environment variables

## GitHub OAuth Authentication and roles authorisation
The application requires the Github client-id and client-secret and redirect Url to be created as environment variables -
```
[GITHUB_CLIENT_ID]
[GITHUB_CLIENT_SECRET]
[GITHUB_REDIRECT_URI]
```
To give a user the writer role (allowing CRUD) an environment variable 
```
[ROLEWRITER_USER]
```
should be created with the users GitHub username as the value.
These environment variables also need to be included in Heroku setting for heroku setup.
Also remeber to create the variable SECRET_KEY for the flask application
Set the environment variable [OAUTHLIB_INSECURE_TRANSPORT]=1 to use HTTP (not recommended on production)

## Hosting the application on Azure app service with CosmosDB database
Create an Azure app Service
Create an an Azure CosmosDB Database with Mongo API
Update Travis-CI environment variables Settings to point to CosmosDB
As we have used MongoDB and docker previously, the environment variables would need to be updated to
point to an azure CosmosDB
```
[MONGO_USERNAME] = <cosmos_account_name>
[MONGO_PASSWORD] = <primarymasterkey>
[MONGO_DB] = <database_name>
[MONGO_URL] = <cosmos_account_name>.mongo.cosmos.azure.com:10255
[MONGO_OPTIONS] = ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000
```
Note also that the all the previous environment variables need to be added to the App service settings 
Add the environment variable 
```
[AZURE_DEPLOY_WEBHOOK] = https://$<deployment_username>:<deployment_password>@<webapp_name>.scm.azurewebsites.net/docker/hook
```
in Travis-CI environment settings to enable Docker image Continuous Deployment.
Note that you would need to enable continous deployment on azure app service deployment center where you can get the
Webhook URL.

## Using Terraform to migrate the ToDo application to azure
Login with Azure CLI
Create an azure blob storage to store the terraform state by running
     ./scripts/createstorage_acct.sh
Run terraform init and terraform apply
Create a service pricipal authentication
```
az ad sp create-for-rbac --name "<SERVICE PRINCIPAL NAME>" --role Contributor --scopes /subscriptions/<SUBSCRIPTION ID>/resourceGroups/<RESOURCE GROUP NAME>
```
Run Terraform apply and copy the webhook URL and update travis-CI AZURE_DEPLOY_WEBHOOK environment variable
Update Travis-CI environment variables Settings with the terraform variables
```
TF_VAR_cosmosdb
TF_VAR_cosmosdb_account
TF_VAR_GITHUB_CLIENT_ID
TF_VAR_GITHUB_CLIENT_SECRET
TF_VAR_GITHUB_REDIRECT_URI
TF_VAR_ROLEWRITER_USER
TF_VAR_SECRET_KEY
TF_VAR_webapp
TF_VERSION=0.14.7
ARM_CLIENT_ID, ARM_TENANT_ID,ARM_SUBSCRIPTION_ID and ARM_CLIENT_SECRET
```
Push you changes and wait for travis to finish
Load the azure application URL in the browser


