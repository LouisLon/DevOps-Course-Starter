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
ENV PORT 5000
RUN pip install poetry && poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN mkdir -p /app/todo_app && touch /app/todo_app/__init__.py && poetry install -n
COPY ./todo_app /app/todo_app
EXPOSE 5000
CMD ["gunicorn", "--chdir", "todo_app", "app:create_app()"]


FROM python:3.8-slim-buster as test

# Install Chrome
RUN apt update && apt-get -y install chromium wget curl unzip
WORKDIR /app
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
&& apt install -y ./google-chrome-stable_current_amd64.deb \
&& rm ./google-chrome-stable_current_amd64.deb
# Install Chromium WebDriver
RUN LATEST=`curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE` \
&& echo "Installing chromium webdriver version ${LATEST}" \
&& wget https://chromedriver.storage.googleapis.com/${LATEST}/chromedriver_linux64.zip \
&& unzip ./chromedriver_linux64.zip
# Install poetry
RUN pip install poetry && poetry config virtualenvs.create true
COPY poetry.lock pyproject.toml /app/
RUN poetry install -n
ENTRYPOINT [ "poetry","run","pytest" ]