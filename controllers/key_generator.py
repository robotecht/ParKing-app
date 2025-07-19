import secrets
import string

def generate_secret_key(length=32):
    """Generate a strong, random secret key."""
    alphabet = string.ascii_letters + string.digits
    # Ensure a good mix of character types
    key = ''.join(secrets.choice(alphabet) for i in range(length))
    return key

# Example usage:
secret_key = generate_secret_key(64) # Generate a 64-character key
print(secret_key)