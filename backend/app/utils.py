import string
import secrets

BASE62_CHARACTERS = string.ascii_letters + string.digits

def generate_random_short_code(length: int = 6) -> str:
    """Generate a random cryptographically secure Base62 string of specified length."""
    return "".join(secrets.choice(BASE62_CHARACTERS) for _ in range(length))
