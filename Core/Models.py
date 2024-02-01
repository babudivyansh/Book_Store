from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, BigInteger, Boolean
from Core.Settings import DATABASE_NAME, DATABASE_PASSWORD

async_engine = create_async_engine(f"postgresql+asyncpg://postgres:{DATABASE_PASSWORD}@localhost:5432/{DATABASE_NAME}", echo=True, future=True)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(250), unique=True)
    password = Column(String(250))
    first_name = Column(String(150))
    last_name = Column(String(150))
    email = Column(String(150))
    phone = Column(BigInteger)
    location = Column(String(150))
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
