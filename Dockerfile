# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 80

# Set the environment variable to run the Flask app
ENV FLASK_APP=main.py

# Command to run the Flask app in development mode
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
