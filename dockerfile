FROM python:3.12

LABEL Maintainer="wrss.wiet"

WORKDIR /app

COPY wrss-bot.py /app
COPY settings.py /app
COPY requirements.txt /app
COPY reaction_utils.py /app
COPY embed.py /app
COPY cogs/ /app/cogs
COPY events/ /app/events

COPY commands_settings/ /app/commands_settings

RUN python3 -m pip install -r requirements.txt

CMD [ "python", "-u", "./wrss-bot.py"]
