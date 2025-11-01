FROM python:3.10.12

WORKDIR /app
COPY ../utils /app/utils
COPY server /app/server
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000

ENTRYPOINT ["python3","-m","server.server"]
