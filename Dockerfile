FROM python:3.13-slim

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy dependencies
COPY pyproject.toml poetry.lock ./

# Install dependencies directly into system since it's a docker container
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application
COPY . .

# Run migrations and the app
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]