import os

seen_emoji_long_id = os.getenv("SEEN_EMOJI_LONG_ID")
doodle_channel_id = int(os.getenv("DOODLE_CHANNEL_ID"))
doodle_seen_reaction = chr(int(os.getenv("DOODLE_SEEN_REACTION"), 0))
notify_role_id = int(os.getenv("NOTIFY_ROLE_ID"))
graphic_role_id = int(os.getenv("GRAPHIC_ROLE_ID"))
client_token = os.getenv("DISCORD_CLIENT_TOKEN")
doodle_links = os.getenv("DOODLE_LINKS").split(',')
