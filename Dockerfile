FROM python:3.9-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y docker.io

COPY . .

EXPOSE 8000

CMD ["python", "server.py"]
