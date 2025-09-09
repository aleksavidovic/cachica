# Use an official Python runtime as a parent image
FROM python:3.13-bookworm

RUN pip install poetry

COPY . .

RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "src/cachica/server.py"]
