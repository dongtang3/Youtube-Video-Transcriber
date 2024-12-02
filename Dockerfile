# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /opt/app

# Copy the current directory contents into the container at /opt/app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose necessary ports
# 7860 for Gradio, 8000 for Prometheus metrics
EXPOSE 7860 8000

# Set environment variable for Gradio server
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Define the command to run the Gradio app
CMD ["python", "/opt/app/app.py"]