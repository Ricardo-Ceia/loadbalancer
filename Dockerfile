FROM python:3.10.12

WORKDIR /app

COPY server.py utils.py .

EXPOSE 5000

ENTRYPOINT ["python3","server.py"]
