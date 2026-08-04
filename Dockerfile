FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY analyze_logs.py .
ENTRYPOINT ["python", "analyze_logs.py"]
