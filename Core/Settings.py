from os import getenv
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")
DATABASE_NAME = getenv("DATABASE_NAME")

PORT = getenv("PORT")
HOST = getenv('localhost')

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
SUPER_KEY = getenv("SUPER_KEY")

email_sender = getenv("EMAIL_SENDER")
email_password = getenv("EMAIL_PASSWORD")

async_engine = create_async_engine(f"postgresql+asyncpg://postgres:{DATABASE_PASSWORD}@localhost:5432/"
                                   f"{DATABASE_NAME}", echo=True, future=True)

