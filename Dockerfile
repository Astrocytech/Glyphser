# Deterministic hello-core runtime image
FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -e .

CMD ["glyphser", "run", "--example", "hello", "--tree"]
