# 1. Base image — Python 3.12 with minimal Linux
FROM python:3.12-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy requirements first (for caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the project
COPY . .

# 6. Expose the port FastAPI runs on
EXPOSE 8000

# 7. Command to start the server
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]