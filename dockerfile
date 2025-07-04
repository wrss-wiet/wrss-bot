FROM python:3.12 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
ENV PATH="/root/.local/bin:$PATH"
COPY --from=builder /root/.local /root/.local
COPY . /app
CMD ["python", "-u", "wrss-bot.py"]
