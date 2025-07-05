import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def pytest_configure():
    """Automatyczne ładowanie .env przed wszystkimi testami"""
    
    current_file = Path(__file__)
    tests_dir = current_file.parent
    repo_dir = tests_dir.parent
    env_file = repo_dir.parent / "env" / "bot.env"
    
    print(f"\n🔍 Szukam pliku .env w: {env_file}")
    
    if env_file.exists():
        load_dotenv(env_file, override=True)
        
        bot_vars = [k for k in os.environ.keys() if any(word in k.upper() 
                    for word in ['DISCORD', 'GUILD', 'CHANNEL', 'ROLE', 'DOODLE'])]
        
        print(f"✅ Załadowano {len(bot_vars)} zmiennych bota z {env_file}")
            
    else:
        print(f"❌ BŁĄD: Nie znaleziono {env_file}")
        print(f"   Sprawdź czy plik istnieje!")
        print(f"   Obecny katalog: {Path.cwd()}")
        
    sys.path.insert(0, str(repo_dir))