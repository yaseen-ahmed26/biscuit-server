# main.py
ORIGINS = [
    "http://127.0.0.1:5500"
]

# users.py, models.py
DEFAULT_PLAYER_STATS = {
    "biscuits": 100.0,
    "total_biscuits": 0.0,
    "total_playtime": 0.0,
    "total_clicks": 0,
    "owned_upgrades": {},
    "owned_achievements": [],
    "prestige": 0,
    "crumbs": 0,
    "owned_unlocks": []
}
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