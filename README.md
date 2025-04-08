# wrss-bot

Discord bot enhancing WRSS WIET &amp; WI workflow

Tested for python 3.12

## Installation

### with docker

1. build image using `docker build -t wrss-bot .`
1. copy `example.docker-compose.yml` to `docker-compose.yml` and set environment variables
1. run container using `docker compose up -d`

### without docker

1. install `direnv`
1. create python venv
1. install packages from `requirements.txt`
1. copy `.sample-envrc` to `.envrc` and set environment variables
1. run `direnv allow` to activate `.envrc`
1. run bot using `python wrss-bot.py`

## Functions

### seen

- adding `seen` reaction to every post on main channel in order to easily show that user has read the message

### threads

- opening thread with name specified in message
- syntax for opening thread with `[thread name]`

```
[thread name]
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
```

### doodle hub

- searches for doodle links in all messages and forwards them to a designated doodle hub channel along with a reference to the original message
- ensures all doodles are in one place so that they can be filled easily :)
- adds a `checkbox` reaction to all forwarded doodles to allow easy marking as completed
- supported doodle links can be specified in `config.py` file

### reaction message

- starts every thread with message showing all reactions to original posts
- made because on mobile devices it was impossible to see reactions to original post while reading thread

### [cd]

- adds `seen` reaction to message with `[cd]` in it even if it is inside a thread
- made when I was posting messages extending discord message length limit, so I had to continue them in threads, but still wanted people to be able to react with `seen` to them

### polls

- automatically adds survey-reactions to post based on message content
- syntax:

```
> - emote0 option-0-description
> - emote1 option-1-description
```

### all-message-notification

- automatically pings users with specified rank in all threads to allow them for receiving notifications about all new messages

## Interactions

### seensettings

- provides a command to configure `seen` reaction settings per channel via a slash command
- options include:
  - **Always:** React to all messages
  - **Threads Only:** React only to messages in threads that meet specific criteria
  - **Off:** Disable `seen` reactions for the channel

Example usage:
```
/seensettings mode: Off channel: XYZ
```

### zamowieniegrafika - modal *template*

- enables users to submit graphic design requests through an interactive modal
- collects details such as event name, description, dimensions, deadline, and additional information
- upon submission, sends an embed with order details and creates a dedicated thread for the request

Usage:
```
/zamowieniegrafika
```
