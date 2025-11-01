FROM python:3.10.12

WORKDIR /app
COPY client /app/client
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000

ENTRYPOINT ["python3","-m","client.client"]
