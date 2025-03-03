#python3 secrete_key.py
#go to ~/.zshrc and add the following statement at the end of the file
#export JWT_SECRET_KEY="985c405a895a4c622acac87bbfde2614d81832ef5370693b3a741a2d4c807684"
import secrets
import os

def generate_secret_key():
    """Generates a secure random secret key."""
    return secrets.token_hex(32)  # 32 bytes (256 bits) is a good length

# Option 1: Generate and store in an environment variable (recommended)
if not os.environ.get("JWT_SECRET_KEY"):
    secret_key = generate_secret_key()
    os.environ["JWT_SECRET_KEY"] = secret_key
    print(f"Generated and set JWT_SECRET_KEY: {secret_key}") #remove in production.
