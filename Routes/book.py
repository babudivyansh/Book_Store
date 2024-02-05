from sanic import Blueprint, response
from sanic_ext import validate, openapi
from sqlalchemy import select
from Core.Models import User, Book
from Core.Schema import BookValidator
from Core.Utils import JWT
from Routes.user import async_session

app = Blueprint('book')
jwt_handler = JWT()


# Middleware for JWT authentication
@app.middleware('request')
async def authenticate(request):
    try:
        token = request.headers.get('authorization')
        if not token:
            return response.json({"message": "Authorization token required"}, status=401)

        payload = jwt_handler.jwt_decode(token)
        user_id = payload.get('user_id')
        user = await async_session.execute(select(User).filter_by(id=user_id))
        user = user.scalars().one_or_none()
        if user is None:
            return response.json({"message": "Invalid token: No user ID found"}, status=401)

        request.ctx.user = user  # Attach user ID to request context

    except Exception as e:
        return response.json({"message": f"Invalid token: {str(e)}"}, status=401)


# Endpoint for book registration
@app.post('/register/')
@openapi.definition(body={'application/json': BookValidator.model_json_schema()}, tag='Book', secured='authorization')
@validate(json=BookValidator)
async def add_book(request, body):
    try:
        async with async_session() as session:
            user = await session.execute(select(User).filter_by(id=request.ctx.user.id))
            user = user.scalars().first()

            if not user:
                return response.json({"message": "User not found"}, status=404)

            data = body.model_dump()
            data.update({'user_id': user.id})
            book_data = Book(**data)
            session.add(book_data)
            await session.commit()
            await session.refresh(book_data)

            return response.json({"message": "Book registered successfully", "book_id": book_data.id}, status=201)

    except Exception as e:
        return response.json({"message": f"Failed to register book: {str(e)}"}, status=500)
