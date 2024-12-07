# Use a Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Set the entry point to start the Flask app
CMD ["python", "run.py"]
