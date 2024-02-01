from sanic import Blueprint, response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from Core.Models import User, async_engine
from Core.Schema import UserValidator, UserLogin
from sanic_ext import validate, openapi
from Core.Utils import Hasher, JWT


jwt_handler = JWT()
app = Blueprint('user')

async_session = sessionmaker(async_engine, class_=AsyncSession)


# Middleware to provide a database session to each request
@app.middleware('request')
async def add_session_to_request(request):
    """
    Description: Middleware to provide an asynchronous database session to each request.
    Parameter: request (Request): Sanic request object.
    Returns: None
    """
    request.ctx.db = async_session()


# Middleware to close the database session after each request
@app.middleware('response')
async def close_session(request, response):
    """
    Description: Middleware to close the asynchronous database session after each request.
    Parameter: request (Request): Sanic request object.
               response (Response): Sanic response object.
    Returns: None
    """
    await request.ctx.db.close()


# Endpoint for user registration
@app.post('/register/')
@openapi.definition(body={'application/json': UserValidator.model_json_schema()})
@validate(json=UserValidator)
async def register_user(request, body):
    """
    Description: Endpoint to register a new user.
    Parameter: request (Request): Sanic request object.
               body (dict): Request body containing user details.
    Returns: JSON response with a message indicating success or failure of user registration.
    """
    try:
        user_validator = UserValidator.model_dump(body)
        user_validator['password'] = Hasher.get_hash_password(user_validator['password'])
        user = User(**user_validator)
        async with async_session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return response.json({"message": "User registered successfully", "user_id": user.id}, status=201)
    except Exception as e:
        return response.json({"message": "Failed to register user", "error": str(e)}, status=500)


@app.post('/login/')
@openapi.definition(body={'application/json': UserLogin.model_json_schema()})
@validate(json=UserLogin)
async def login(request, body: UserLogin):
    """
    Endpoint to authenticate a user.

    :param request: Sanic request object.
    :param body: UserLogin schema containing username and password.
    :return: JSON response indicating success or failure of authentication.
    """
    try:
        async with async_session() as session:
            user = await session.execute(select(User).filter(User.username == body.username))
            user = user.scalars().first()
            if not user or not Hasher.verify_password(body.password, user.password):
                return response.json({"message": "Invalid username or password"}, status=401)
            token = jwt_handler.jwt_encode({'user_id': user.id})
            return response.json({"message": "Login successful", "user_id": user.id, 'access_token': token}, status=200)

    except Exception as e:
        return response.json({"message": "Failed to authenticate user", "error": str(e)}, status=500)
