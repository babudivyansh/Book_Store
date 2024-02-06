from sanic import Blueprint, response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from Core.Models import User
from Core.Schema import UserValidator, UserLogin
from sanic_ext import validate, openapi
from Core.Settings import async_engine, SUPER_KEY
from Core.Utils import Hasher, JWT
from tasks import send_verification_email

jwt_handler = JWT()
app = Blueprint('user')

async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


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
async def close_session(request):
    """
    Description: Middleware to close the asynchronous database session after each request.
    Parameter: request (Request): Sanic request object.
               response (Response): Sanic response object.
    Returns: None
    """
    await request.ctx.db.close()


# Endpoint for user registration
@app.post('/register/')
@openapi.definition(body={'application/json': UserValidator.model_json_schema()}, tag='User')
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
        user_super_key = user_validator['is_superuser']
        if user_super_key == SUPER_KEY:  # key is in the form of string
            user_validator.update({'is_superuser': True})
        # user_validator.pop('is_superuser')
        user = User(**user_validator)
        async with async_session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            request.ctx.user_id = user.id
            token = jwt_handler.jwt_encode({'user_id': user.id})
            send_verification_email(token, user.email)
        return response.json({"message": "User registered successfully", "user_id": user.id}, status=201)
    except Exception as e:
        return response.json({"message": "Failed to register user", "error": str(e)}, status=500)


@app.post('/login/')
@openapi.definition(body={'application/json': UserLogin.model_json_schema()}, tag='User')
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
            if user.is_verified is False:
                return response.json({"message": "User not verified"}, status=401)
            token = jwt_handler.jwt_encode({'user_id': user.id})
            return response.json({"message": "Login successful", "user_id": user.id, 'access_token': token}, status=200)

    except Exception as e:
        return response.json({"message": "Failed to authenticate user", "error": str(e)}, status=500)


@app.get('/verify')
@openapi.definition(parameter={'name': 'token', 'required': True}, tag='User')
@validate(query_argument='token')
async def verify_user(request):
    """
    Description: Endpoint to verify a user based on the provided token.
    Parameter: token (str): Token string obtained from the verification link.
    Returns: JSON response indicating the success or failure of user verification.
    """
    try:
        token = request.args.get('token')
        if not token:
            return response.json({"message": "Token is required"}, status=400)

        decoded_token = jwt_handler.jwt_decode(token)
        user_id = decoded_token.get('user_id')

        async with async_session() as session:
            user = await session.execute(select(User).filter_by(id=user_id, is_verified=False))
            user = user.scalars().first()
            if not user:
                return response.json({"message": "User already verified or not found"}, status=400)

            user.is_verified = True
            await session.commit()
            return response.json({"message": "User verified successfully", "user_id": user.id}, status=200)

    except Exception as e:
        return response.json({"message": "Failed to verify user", "error": str(e)}, status=500)
