FROM python:3.12-slim

# Root of manage.py
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project files
COPY . .

# Expose the Django dev port
EXPOSE 8000

# Run the development server (for testing)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
