"""
@Author: Divyansh Babu

@Date: 2024-01-31 12:40

@Last Modified by: Divyansh Babu

@Last Modified time: 2024-02-01 12:37

@Title : Book Store app using Sanic.
"""
from sanic import Sanic

from Routes.book import add_book
from Routes.user import register_user, login, verify_user

app = Sanic(__name__)


app.ext.openapi.add_security_scheme(
    "authorization",
    "http",
    # scheme="bearer",
    bearer_format="JWT"
)


# Route the user registration API
app.add_route(login, '/login/', methods=['POST'])
app.add_route(register_user, '/register/', methods=['POST'])
app.add_route(verify_user, '/verify')

app.add_route(add_book, '/add_book', methods=['POST'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
