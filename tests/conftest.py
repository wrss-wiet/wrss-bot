import os
from pathlib import Path
from dotenv import load_dotenv

def find_env_file(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        candidate = parent / "env" / "bot.env"
        if candidate.exists():
            return candidate
    return None

here = Path(__file__).resolve()
env_file = find_env_file(here)

if env_file:
    load_dotenv(env_file, override=True)
    print(f"✅ Załadowano env z: {env_file}")
else:
    print("ℹ️  Nie znaleziono env/bot.env.")
