# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install poetry globally
RUN pip install poetry

# Set the working directory specifically for the agent
WORKDIR /app/packages/iris-agent

# Copy only the necessary configuration for Iris
COPY ./packages/iris-agent/pyproject.toml ./packages/iris-agent/poetry.lock* ./

# Copy the dependency package that Iris needs
# This assumes phoenix_event_bridge is a local dependency
COPY ./packages/phoenix_event_bridge /app/packages/phoenix_event_bridge

# Install dependencies for Iris ONLY
# This is a more robust way to install in a monorepo context
RUN poetry config virtualenvs.create false &&     poetry install --only main --no-interaction --no-ansi --no-root

# Copy the application source code for Iris
COPY ./packages/iris-agent/ .

# Command to run the application from the correct directory
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

