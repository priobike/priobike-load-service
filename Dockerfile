FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Postgres client to check liveness of the database
RUN apt-get update && apt-get install -y postgresql-client

# Install Poetry as the package manager for this application
RUN pip install poetry

WORKDIR /code

# Install Python dependencies separated from the
# run script to enable Docker caching
ADD pyproject.toml /code
RUN poetry install --no-interaction --no-ansi --no-dev

COPY . /code
