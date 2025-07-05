import unittest
import os
import sys
sys.path.append('..')

class TestRealEnvironment(unittest.TestCase):
    """Testy zmiennych środowiskowwych"""
    
    def setUp(self):
        """Lista wszystkich wymaganych zmiennych z settings.py"""
        self.required_env_vars = [
            'DISCORD_CLIENT_TOKEN',
            'MAIN_GUILD_ID', 
            'SEEN_EMOJI_LONG_ID',
            'DOODLE_CHANNEL_ID',
            'DOODLE_SEEN_REACTION',
            'NOTIFY_ROLE_ID',
            'GRAPHIC_ROLE_ID',
            'DOODLE_LINKS',
            'VOICE_CREATOR',
            'VC_CATEGORY', 
            'EVENTS_CATEGORY',
            'EVENTS_ARCHIVE',
            'DEF_ARCHIVE'
        ]
        
        self.numeric_vars = [
            'MAIN_GUILD_ID', 'DOODLE_CHANNEL_ID', 'NOTIFY_ROLE_ID',
            'GRAPHIC_ROLE_ID', 'VOICE_CREATOR', 'VC_CATEGORY',
            'EVENTS_CATEGORY', 'EVENTS_ARCHIVE', 'DEF_ARCHIVE'
        ]
        
        self.hex_vars = ['DOODLE_SEEN_REACTION']
    
    def test_all_required_vars_present(self):
        """Sprawdza czy wszystkie wymagane zmienne są obecne"""
        missing_vars = []
        for var in self.required_env_vars:
            if var not in os.environ:
                missing_vars.append(var)
        
        if missing_vars:
            self.fail(f"Brakuje zmiennych środowiskowych: {', '.join(missing_vars)}")
    
    def test_all_required_vars_not_empty(self):
        """Sprawdza czy żadna zmienna nie jest pusta"""
        empty_vars = []
        for var in self.required_env_vars:
            value = os.getenv(var, '')
            if not value or value.strip() == '':
                empty_vars.append(var)
        
        if empty_vars:
            self.fail(f"Puste zmienne środowiskowe: {', '.join(empty_vars)}")
    
    def test_numeric_vars_are_valid_numbers(self):
        """Sprawdza czy zmienne numeryczne można skonwertować na int"""
        invalid_vars = []
        for var in self.numeric_vars:
            value = os.getenv(var)
            if value is None:
                invalid_vars.append(f"{var}: brak zmiennej")
                continue
                
            try:
                int_value = int(value)
                if int_value < 0:
                    invalid_vars.append(f"{var}: wartość ujemna ({value})")
            except ValueError:
                invalid_vars.append(f"{var}: nie jest liczbą ({value})")
        
        if invalid_vars:
            self.fail(f"Nieprawidłowe zmienne numeryczne: {'; '.join(invalid_vars)}")
    
    def test_hex_vars_are_valid_hex(self):
        """Sprawdza czy zmienne hex można skonwertować"""
        invalid_vars = []
        for var in self.hex_vars:
            value = os.getenv(var)
            if value is None:
                invalid_vars.append(f"{var}: brak zmiennej")
                continue
                
            try:
                int(value, 0)
            except ValueError:
                invalid_vars.append(f"{var}: nieprawidłowy format hex ({value})")
        
        if invalid_vars:
            self.fail(f"Nieprawidłowe zmienne hex: {'; '.join(invalid_vars)}")
    
    def test_discord_token_format(self):
        """Sprawdza format tokena Discord"""
        token = os.getenv('DISCORD_CLIENT_TOKEN')
        self.assertIsNotNone(token, "DISCORD_CLIENT_TOKEN nie może być None")
        
        parts = token.split('.')
        self.assertEqual(len(parts), 3, 
                        f"Token musi mieć 3 części oddzielone kropkami, ma {len(parts)}")
        
        self.assertGreater(len(parts[0]), 10, "ID bota musi mieć odpowiednią długość")
    
    def test_doodle_links_format(self):
        """Sprawdza format linków Doodle"""
        links_str = os.getenv('DOODLE_LINKS')
        self.assertIsNotNone(links_str, "DOODLE_LINKS nie może być None")
        
        links = links_str.split(',')
        invalid_links = []
        
        for link in links:
            link = link.strip()
            if not link.startswith('https://'):
                invalid_links.append(f"'{link}' nie zaczyna się od https://")
            if '.' not in link:
                invalid_links.append(f"'{link}' nie zawiera domeny")
        
        if invalid_links:
            self.fail(f"Nieprawidłowe linki: {'; '.join(invalid_links)}")
    
    def test_settings_import_with_real_env(self):
        """Sprawdza czy settings.py importuje się z prawdziwymi zmiennymi"""
        try:
            import settings
            
            required_attrs = [
                'main_guild_id', 'seen_emoji_long_id', 'doodle_channel_id',
                'doodle_seen_reaction', 'notify_role_id', 'graphic_role_id',
                'client_token', 'doodle_links', 'voice_creator', 'vc_category',
                'events_category', 'events_archive', 'def_archive'
            ]
            
            missing_attrs = []
            for attr in required_attrs:
                if not hasattr(settings, attr):
                    missing_attrs.append(attr)
            
            if missing_attrs:
                self.fail(f"Brakuje atrybutów w settings: {', '.join(missing_attrs)}")
                
        except Exception as e:
            self.fail(f"Import settings nie powiódł się: {e}")

if __name__ == '__main__':
    unittest.main()
