# ------- IMPORTS -------
from nanoid import generate

# ------- SETUP -------
alphanumeric = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

# ------- FUNCTIONS -------
def generate_id(size: int = 5):
    return generate(alphanumeric, size)
