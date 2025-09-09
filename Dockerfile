# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock (if using poetry)
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the source code
COPY src/ ./src/

# Expose the port CachePy will run on
EXPOSE 6379

# Run the application
CMD ["poetry", "run", "python", "src/cachepy/server.py"]
# Or, if you made it an entry point:
# CMD ["cachepy"]

