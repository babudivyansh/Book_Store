from sanic import Blueprint, response
from sanic_ext import openapi, validate
from sqlalchemy import select
from Core.Models import Book, User
from Core.Schema import BookValidator
from Core.Utils import JWT
from Routes.user import async_session

app = Blueprint("book")
jwt_handler = JWT()


# Middleware for JWT authentication
@app.middleware("request")
async def authenticate(request):
    try:
        token = request.headers.get("authorization").split(" ")[1]
        if not token:
            return response.json({"message": "Authorization token required"}, status=401)

        payload = jwt_handler.jwt_decode(token)
        user_id = payload.get("user_id")
        user = await async_session().execute(select(User).filter_by(id=user_id))
        user = user.scalars().one_or_none()
        if user is None:
            return response.json({"message": "Invalid token: No user ID found"}, status=401)

        request.ctx.user = user  # Attach user ID to request context

    except Exception as e:
        return response.json({"message": f"Invalid token: {str(e)}"}, status=401)


# Endpoint for book registration
@app.post("/create_book/")
@openapi.definition(
    body={"application/json": BookValidator.model_json_schema()},
    tag="Book",
    secured="authorization",
)
@validate(json=BookValidator)
async def add_book(request, body):
    try:
        async with async_session() as session:
            user = await session.execute(select(User).filter_by(id=request.ctx.user.id))
            user = user.scalars().first()

            if not user:
                return response.json({"message": "User not found"}, status=404)
            if user and not user.is_superuser:
                return response.json({"message": "Sorry You are Not a Super User"}, status=400)

            data = body.model_dump()
            data.update({"user_id": user.id})
            book_data = Book(**data)
            session.add(book_data)
            await session.commit()
            await session.refresh(book_data)
            return response.json(
                {"message": "Book registered successfully", "book_id": book_data.id}, status=201
            )

    except Exception as e:
        return response.json({"message": f"Failed to register book: {str(e)}"}, status=500)


# Read (GET)
@app.get('/get_all_book')
@openapi.definition(tag='Book', secured='authorization')
async def get_book(request):
    try:
        async with async_session() as session:
            books = await session.execute(select(Book))
            books = books.scalars().all()

            if not books:
                return response.json({"message": "No books found"}, status=404)

            # Create a list to store information about each book
            books_info = []
            for book in books:
                book_info = {
                    "book_id": book.id,
                    "book_name": book.book_name,
                    "author": book.author,
                    "price": book.price,
                    "quantity": book.quantity
                }
                books_info.append(book_info)

            # Return information about all books
            return response.json({"books": books_info}, status=200)

    except Exception as e:
        return response.json({"message": f"Failed to retrieve books: {str(e)}"}, status=500)


# Update (PUT/PATCH)
@app.put('/<book_id:int>')
@openapi.definition(body={'application/json': BookValidator.model_json_schema()}, tag='Book', secured='authorization')
@validate(json=BookValidator)
async def update_book(request, body, book_id):
    try:
        async with async_session() as session:
            book = await session.execute(select(Book).filter_by(id=book_id, user_id=request.ctx.user.id))
            book = book.scalars().first()

            if not book:
                return response.json({"message": "Book not found"}, status=404)
            if book and not request.ctx.user.is_superuser:
                return response.json({"message": "Sorry You are Not a Super User"}, status=400)

            # Update book information
            data = body.model_dump()
            [setattr(book, key, value) for key, value in data.items()]
            await session.commit()
            await session.refresh(book)

            return response.json({"message": "Book updated successfully", "book_id": book_id})

    except Exception as e:
        return response.json({"message": f"Failed to update book: {str(e)}"}, status=500)


# Delete (DELETE)
@app.delete('/<book_id:int>')
@openapi.definition(tag='Book', secured='authorization')
async def delete_book(request, book_id: int):  # Ensure the function signature includes the book_id parameter
    try:
        async with async_session() as session:
            book = await session.execute(select(Book).filter_by(id=book_id, user_id=request.ctx.user.id))
            book = book.scalars().first()

            if not book:
                return response.json({"message": "Book not found"}, status=404)
            if book and not request.ctx.user.is_superuser:
                return response.json({"message": "Sorry You are Not a Super User"}, status=400)

            # Delete book
            await session.delete(book)
            await session.commit()

            return response.json({"message": "Book deleted successfully", "book_id": book_id})

    except Exception as e:
        return response.json({"message": f"Failed to delete book: {str(e)}"}, status=500)
