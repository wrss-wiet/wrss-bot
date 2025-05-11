# wrss-bot

Discord bot enhancing WRSS WIET &amp; WI workflow

Tested for python 3.12

## Installation

### with docker

1. build the image using `docker build -t wrss-bot .`
1. copy `example.docker-compose.yml` to `docker-compose.yml` and set environment variables
1. run container using `docker compose up -d`

### without docker

1. install `direnv`
1. create python venv
1. install packages from `requirements.txt`
1. copy `.sample-envrc` to `.envrc` and set environment variables
1. run `direnv allow` to activate `.envrc`
1. run bot using `python wrss-bot.py`

## Configuration Files

The bot requires three JSON files in the project root:

- `role_settings.json`  
- `embed_settings.json`  
- `seen_settings.json`

If they do not exist, the bot will create empty ones, but you should seed them with a basic structure to avoid errors in `/embed` commands.

> **⚠ Warning:** Ensure *embed_settings* file contain at least the default structure below before first use.

### Sample `embed_settings.json` structure

```json
{
  "default": {
    "title": "",
    "description": "",
    "url": "",
    "color": "2fc8b6",
    "footer": {
      "text": "",
      "icon_url": ""
    },
    "image": "",
    "thumbnail": "",
    "author": {
      "name": "",
      "url": "",
      "icon_url": ""
    },
    "fields": [
      {
        "name": "",
        "value": "",
        "inline": false
      }
    ],
    "buttons": [
      {
        "label": "",
        "emoji": "",
        "style": "link",
        "url": "",
        "embed": {}
      }
    ]
  }
}
```

## Features

- **Seen Reactions**  
  Configurable `seen` reaction per channel via `/seensettings` in order to easily show that user has read the message.  

- **Thread Creation**  
  Auto-opens a thread when a message starts with `[thread name]`.  

- **Doodle Hub**  
  Forwards detected Doodle links to a dedicated hub channel with context and reference to original message. Ensures all doodles links are in one place so that they could be filled easily. Adds a `checbox` emoji reaction to all forwarded doodles to allow easy marking as completed. Supported doodle links can be specified in `example.docker-compose.yml`.  

- **Reaction Summary**  
  The first message in every thread shows all reactions on the source message. Made because on mobile devices it was impossible to see reactions to original post while reading thread.

- **Continued Discussion `[cd]`**  
  Adds `seen` reaction to posts with `[cd]` inside a thread.

- **Polls**  
  Auto-adds reaction options based on message content.
  Syntax:

```discord
> - emote0 option-0-description
> - emote1 option-1-description
```

- **All-Message Notification**  
Automatically pings users with a specified role in every thread for full visibility and receiving notifications.

## Slash Commands

All commands below are registered **only** on the server where the bot is installed.

### /seensettings

Configure `seen` reaction behavior per channel.

- **channel**: TextChannel (optional)  
- **mode**: `Always` / `ThreadsOnly` / `Off` (optional)  
- **scope**: `current` / `all` (default: `all`) *- to view the current configuration*

Example:  

```discord
/seensettings mode:Off channel:general
```

> **Note:** The command above will disable adding reactions to any message in the `general` channel.

### /role

Manage role groups via several subcommands:

- **/role list**  
  Lists all configured role groups.

- **/role create `<group_name>`**  
  Creates a new role group.

- **/role add `<group_name>` `<@role>` `<emoji>` `[description]`**  
  Adds a role to a group with a button emoji.

- **/role remove `<group_name>` `<emoji>`**  
  Removes a role from a group.

- **/role show `<group_name>`**  
  Sends an embed with buttons to assign or remove roles.

### /embed

Save and send rich embeds via configuration:

- **/embed list**  
  Lists all saved embed keys.

- **/embed save `<embed_key>`**  
  Opens a modal to build and save a new embed under `embed_key`.

- **/embed send `<embed_key>`**  
  Sends the saved embed to the channel (autocomplete enabled).

### /zamowieniegrafik

Interactive modal for graphic design orders as a template. Collects:

- `Event Name`  
- `What`  
- `Dimensions`  
- `Deadline`  
- `Theme & Additional Info` (optional)

On submit, it posts an embed and creates a thread.

#### Edit Mode

You can pass an optional `edytuj` parameter to update an existing order:

```discord
/zamowieniegrafik edit:<message_id>
```

- Opens the modal pre-filled with data from the specified embed message - *you don't have to fill in all the information again.*
- On submit, edits the original embed (fix typos, update deadline, etc.)  
