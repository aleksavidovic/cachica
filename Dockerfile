# ---- Builder Stage ----
# Use a full Python image that includes common build tools.
FROM python:3.13-slim-trixie AS builder

# Install pipx to manage CLI tools like poetry in an isolated environment.
RUN pip install pipx
RUN pipx ensurepath
ENV PATH="/root/.local/bin:$PATH"

# Install poetry using pipx.
RUN pipx install poetry==2.1.4

# Set environment variables for Poetry.
# - Turn off interactive prompts.
# - Tell Poetry to create the virtual environment inside the project folder (.venv)
#   for easy copying later.
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

WORKDIR /app

# Copy only the files needed for dependency installation first.
# This leverages Docker's layer caching. This layer is only rebuilt
# when your dependencies change.
COPY pyproject.toml poetry.lock ./

# Install dependencies into the local .venv directory.
# --without dev: Skip development dependencies (like pytest, ruff).
# --no-root: Don't install the project package itself, only its dependencies.
RUN poetry install --without dev --no-root

# ---- Final Stage ----
# Use a slim image for a smaller final footprint.
FROM python:3.13-slim-trixie AS final

# Create a non-root user and group for security.
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid 1001 -m appuser

WORKDIR /app

# Copy the virtual environment with all the dependencies from the builder stage.
COPY --from=builder --chown=appuser:appgroup /app/.venv ./.venv

# Copy the application source code.
COPY --chown=appuser:appgroup src ./src

# Set the PATH to include the virtual environment's bin directory.
# This allows us to run `python` directly from the venv.
ENV PATH="/app/.venv/bin:$PATH"

# Switch to the non-root user.
USER appuser

# Set the command to run the application.
# We no longer need "poetry run" because the correct python interpreter
# is now on the PATH.
CMD ["python", "src/cachica/server.py"]
