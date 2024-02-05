from jose import jwt
from passlib.context import CryptContext
from Core import Settings
from datetime import datetime, timedelta
import pytz
import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(filename='./fundoo_notes.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()


class Hasher:
    @staticmethod
    def get_hash_password(plain_password):
        return pwd_context.hash(plain_password)

    @staticmethod
    def verify_password(plain_password, hash_password):
        return pwd_context.verify(plain_password, hash_password)


class JWT:
    @staticmethod
    def jwt_encode(payload: dict):
        if 'exp' not in payload:
            payload.update(exp=datetime.now(pytz.utc) + timedelta(hours=1), iat=datetime.now(pytz.utc))
        return jwt.encode(payload, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)

    @staticmethod
    def jwt_decode(token):
        try:
            return jwt.decode(token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        except jwt.JWTError as e:
            logger.exception(e)
