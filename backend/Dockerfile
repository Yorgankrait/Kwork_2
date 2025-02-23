# Use the official Python image with Alpine Linux
FROM python:3.12.4-alpine

# Install system dependencies
RUN apk update && \
  apk add --no-cache \
  build-base \
  postgresql-dev \
  libffi-dev \
  openssl-dev \
  bash \
  su-exec

# Set working directory
WORKDIR /backend

# Copy requirements.txt and install dependencies
COPY ./requirements.txt /temp/requirements.txt
RUN pip install --upgrade pip && \
  pip install -r /temp/requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 (if your application uses this port)
EXPOSE 8000

# Create a non-root user
RUN adduser --disabled-password admin-user

RUN chown admin-user:root "celerybeat-schedule"
# Switch to the non-root user
USER admin-user
