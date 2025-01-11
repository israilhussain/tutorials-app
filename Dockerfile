# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy your project files into the /app directory inside the container
COPY . /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Command to start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
