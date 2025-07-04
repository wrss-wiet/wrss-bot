FROM python:3.12 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
ENV PATH=/root/.local/bin:$PATH

COPY --from=builder /root/.local /root/.local

COPY wrss-bot.py settings.py reaction_utils.py embed.py ./
COPY requirements.txt .
COPY cogs/ cogs/
COPY events/ events/
COPY commands_settings/ commands_settings/

CMD ["python", "-u", "wrss-bot.py"]
