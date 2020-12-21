FROM python:3.8.6-slim-buster as development

WORKDIR /app
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_APP todo_app/app.py
ENV FLASK_ENV development
RUN pip install poetry && poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN poetry install -n
EXPOSE 5000
CMD ["flask", "run"]


FROM python:3.8-slim-buster as production

RUN mkdir /app 
WORKDIR /app
ENV PYTHONPATH=/app 
ENV PYTHONUNBUFFERED True
ENV PYTHONHASHSEED 0
RUN pip install poetry && poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN mkdir -p /app/todo_app && touch /app/todo_app/__init__.py && poetry install -n
COPY ./todo_app /app/todo_app
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "todo_app", "app:create_app()"]