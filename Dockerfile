FROM python:3.10-alpine

RUN adduser -D myuser

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install --upgrade pip
RUN pip install poetry && poetry config virtualenvs.create false

RUN poetry install --only main
USER myuser

EXPOSE 8000

COPY . /app/

ENV PYTHONUNBUFFERED 1
