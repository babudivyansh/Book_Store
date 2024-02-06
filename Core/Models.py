from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, BigInteger, Boolean, ForeignKey

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
    book = relationship('Book', back_populates='user')
    cart = relationship('Cart', back_populates='user')

    def __str__(self):
        return self.username


class Book(Base):
    __tablename__ = 'book'

    id = Column(BigInteger, primary_key=True, index=True)
    book_name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(BigInteger, nullable=False)
    quantity = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', back_populates='book')
    cart_items = relationship('CartItems', back_populates='book')

    def __str__(self):
        return self.book_name


class Cart(Base):
    __tablename__ = 'cart'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    total_price = Column(BigInteger, default=0)
    total_quantity = Column(BigInteger, default=0)
    is_ordered = Column(Boolean, default=False)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', back_populates='cart')
    cart_items = relationship('CartItems', back_populates='cart')


class CartItems(Base):
    __tablename__ = 'cart_items'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    price = Column(BigInteger, default=0)
    quantity = Column(BigInteger, default=0)
    book_id = Column(BigInteger, ForeignKey('book.id', ondelete='CASCADE'), nullable=False, unique=True)
    cart_id = Column(BigInteger, ForeignKey('cart.id', ondelete='CASCADE'), nullable=False)
    book = relationship('Book', back_populates='cart_items')
    cart = relationship('Cart', back_populates='cart_items')
