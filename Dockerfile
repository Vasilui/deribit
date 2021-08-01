FROM python:3.9

RUN apt-get update
RUN apt-get install default-mysql-client -y
RUN mkdir /var/deribit && touch /var/deribit/settings.json
RUN pip3 install poetry

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
RUN poetry shell

COPY . /app