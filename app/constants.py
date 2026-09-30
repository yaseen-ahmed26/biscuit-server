# main.py
ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "https://yaseen-ahmed26.github.io"
]

# users.py, models.py
SAVE_ID_LENGTH = 32

# codes.py, schemas.py
LOGIN_CODE_LENGTH = 7
LOGIN_CODE_EXPIRATION_MINS = 2

# helpers.py
ALPHANUMERIC_SET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

# security.py
REFRESH_TOKEN_LENGTH = 64

# models.py
USERNAME_MAX_LENGTH = 24
EMAIL_MAX_LENGTH = 30
PASSWORD_HASH_MAX_LENGTH = 200

# database.py
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./biscuit.db"

# saves.py
AVERAGE_CLICK_SPEED_SECOND = 5
MAX_AMOUNT_BISCUITS_CLICK = 250
BISCUIT_BUFFER = 2
MAX_SESSION_LENGTH = 240