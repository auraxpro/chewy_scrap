import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://chewy_user:chewy_password@localhost:5432/chewy_db'
)

POSTGRES_USER = os.getenv('POSTGRES_USER', 'chewy_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'chewy_password')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'chewy_db')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

