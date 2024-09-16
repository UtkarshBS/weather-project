FROM python:3.10.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# exposing the flask port
EXPOSE 5000

# running the api file
CMD ["python", "scripts/api.py"]
