from os import getenv

from dotenv import load_dotenv

load_dotenv()

DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")
DATABASE_NAME = getenv("DATABASE_NAME")

PORT = getenv("PORT")
HOST = getenv('localhost')
