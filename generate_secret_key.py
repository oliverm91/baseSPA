import secrets
import string
import re
import random
from pathlib import Path

def update_secret_key():
    # Character set requested: a-z A-Z 0-9 ! @ * - _ = + ^ , . : ; " [ ] ( ) { }
    chars = string.ascii_letters + string.digits + '!@*-_=+^,.:;[](){}'
    length = random.randint(50, 100)
    
    # Use cryptographically secure module (secrets) instead of random
    new_key = ''.join(secrets.choice(chars) for _ in range(length))
    
    env_file = Path('.env')
    if not env_file.exists():
        print("Error: .env file not found in the current directory!")
        return

    content = env_file.read_text(encoding='utf-8')
    
    # Write raw string into the .env parser without quotes
    new_line = f"SECRET_KEY={new_key}"
    
    if re.search(r'^SECRET_KEY=.*$', content, flags=re.MULTILINE):
        content = re.sub(r'^SECRET_KEY=.*$', new_line, content, flags=re.MULTILINE)
    else:
        content += f"\n{new_line}\n"
        
    env_file.write_text(content, encoding='utf-8')
    print(f"Successfully generated a new SECRET_KEY in .env!")

if __name__ == '__main__':
    update_secret_key()
