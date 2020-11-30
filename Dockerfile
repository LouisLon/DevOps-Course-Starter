FROM python:3.8-slim-buster as development

WORKDIR /code

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=todo_app/app.py
ENV FLASK_ENV=development

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /code/

RUN poetry install -n
COPY . .

EXPOSE 5000
CMD ["flask", "run"]


FROM python:3.8-slim-buster as prod

RUN mkdir /app 
WORKDIR /app

ENV PYTHONPATH=/app 
ENV PYTHONUNBUFFERED True
ENV PYTHONHASHSEED 0

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /app/

RUN mkdir -p /app/src/todo_app
RUN touch /app/src/todo_app/__init__.py

RUN poetry install -n
COPY ./todo_app /app/src/todo_app

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "src/todo_app", "app:create_app()"]