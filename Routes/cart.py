from sanic import Blueprint, response
from sqlalchemy import select
from Core.Models import Cart, Book, CartItems, User
from Core.Schema import CartItemsValidator
from Routes.user import async_session, jwt_handler
from sanic_ext import openapi, validate

cart = Blueprint('cart')


@cart.middleware("request")
async def authenticate(request):
    """
    Middleware function for JWT authentication.

    Args:
        request: Request object.

    Returns:
        JSON response indicating the success or failure of user verification.
    """
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


# Endpoint to add a book to the cart
@cart.post('/add')
@openapi.definition(body={'application/json': CartItemsValidator.model_json_schema()}, tag='Cart',
                    secured="authorization")
@validate(json=CartItemsValidator)
async def add_book_to_cart(request, body):
    """
    Endpoint to add a book to the cart.

    Args:
        request: Request object.
        body: Request body containing book information.

    Returns:
        JSON response indicating the success or failure of adding a book to the cart.
    """
    try:
        async with async_session() as session:
            cart_data = await session.execute(select(Cart).filter_by(user_id=request.ctx.user.id))
            cart_data = cart_data.scalars().one_or_none()

            if cart_data is None:
                cart_data = Cart(user_id=request.ctx.user.id)
                session.add(cart_data)

            book_data = await session.execute(select(Book).filter_by(id=body.book_id))
            book_data = book_data.scalars().one_or_none()

            if book_data is None:
                raise Exception("This book is not present")

            if body.quantity > book_data.quantity:
                raise Exception(f"This book is present and there Quantity is {book_data.quantity}")

            books_price = body.quantity * book_data.price

            cart_items_data = await session.execute(select(CartItems).filter_by(book_id=body.book_id))
            cart_items_data = cart_items_data.scalars().one_or_none()

            if cart_items_data is None:
                cart_items_data = CartItems(price=books_price, quantity=body.quantity, book_id=book_data.id,
                                            cart_id=cart_data.id)
                session.add(cart_items_data)
            else:
                cart_data.total_price -= cart_items_data.price
                cart_data.total_quantity -= cart_items_data.quantity

            cart_data.total_price += books_price
            cart_data.total_quantity += body.quantity

            await session.commit()
            await session.refresh(cart_data)
            await session.refresh(cart_items_data)

            return response.json({'message': 'Book added on cart Successfully', 'status': 201})
    except Exception as ex:
        return response.json({'message': str(ex), 'status': 400})


@cart.get('/get')
@openapi.definition(response={'200': {'application/json': CartItemsValidator.model_json_schema()}}, tag='Cart',
                    secured="authorization")
async def get_cart_details(request):
    """
    Endpoint to get cart details.

    Args:
        request: Request object.

    Returns:
        JSON response containing cart details.
    """
    try:
        async with async_session() as session:
            cart_data = await session.execute(select(Cart).filter_by(user_id=request.ctx.user.id))
            cart_data = cart_data.scalars().all()

            if cart_data is None:
                raise Exception("This cart is not present")

            total_quantity = sum(cart1.total_quantity for cart1 in cart_data)
            if total_quantity == 0:
                raise Exception("The cart is empty")

            cart_info = []
            for i in cart_data:
                cart_data = {
                    "price": i.total_price,
                    "quantity": i.total_quantity
                }
                cart_info.append(cart_data)
            return response.json({'message': "Cart Data found Successfully", 'status': 200, 'data': cart_data})
    except Exception as ex:
        return response.json({'message': str(ex), 'status': 400})


@cart.get('/get/<cart_id:int>')
@openapi.definition(response={200: {'application/json': CartItemsValidator.model_json_schema()}}, tag='Cart',
                    secured="authorization")
async def get_all_cart_items_details(request, cart_id):
    """
    Endpoint to get details of all cart items.

    Args:
        request: Request object.
        cart_id (int): ID of the cart.

    Returns:
        JSON response containing details of all cart items.
    """
    try:
        async with async_session() as session:
            cart_data = await session.execute(select(Cart).filter_by(id=cart_id, user_id=request.ctx.user.id))
            cart_data = cart_data.scalars().one_or_none()

            if cart_data is None:
                return response.json({'message': 'Cart is empty', 'status': 400})

            card_items_data = await session.execute(select(CartItems).filter_by(cart_id=cart_id))
            card_items_data = card_items_data.scalars().all()

            serialized_card_items_data = []
            for item in card_items_data:
                serialized_item = {
                    'id': item.id,
                    'book_id': item.book_id,
                    'quantity': item.quantity,
                    'price': item.price,
                    'cart_id': item.cart_id
                }
                serialized_card_items_data.append(serialized_item)

            return response.json({'message': 'All cart items get successfully', 'status': 200,
                                  'data': serialized_card_items_data})
    except Exception as ex:
        return response.json({'message': str(ex), 'status': 400})


@cart.get('/confirm')
@openapi.definition(tag='Cart', secured="authorization")
async def confirm_order(request):
    """
    Endpoint to confirm the order.

    Args:
        request: Request object.

    Returns:
        JSON response indicating the success or failure of order confirmation.
    """
    try:
        async with async_session() as session:
            cart_data = await session.execute(select(Cart).filter_by(user_id=request.ctx.user.id))
            cart_data = cart_data.scalars().one_or_none()

            if cart_data is None:
                return response.json({'message': 'The Cart is Empty', 'status': 400})

            cart_items_details = await session.execute(select(CartItems).filter_by(cart_id=cart_data.id))
            cart_items_details = cart_items_details.scalars().all()

            cart_data.is_ordered = True

            user_data = await session.execute(select(User).filter_by(id=request.ctx.user.id))
            user_data = user_data.scalars().one_or_none()

            await session.commit()
            return response.json({'message': 'Order Confirmation Successfully', 'status': 200})
    except Exception as ex:
        return response.json({'message': str(ex), 'status': 400})
