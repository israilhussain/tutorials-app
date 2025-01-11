# Use the official Python image
FROM python:3.11-slim

# Set the working directory to match your desired structure
WORKDIR /tutorials-app

# Copy requirements.txt into the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project folder into the container
COPY . .

# Set the working directory to the app directory
WORKDIR /tutorials-app/app

# Expose the port
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
