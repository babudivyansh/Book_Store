"""
@Author: Divyansh Babu

@Date: 2024-01-31 12:40

@Last Modified by: Divyansh Babu

@Last Modified time: 2024-02-01 12:37

@Title : Book Store app using Sanic.
"""
from sanic import Sanic
from Routes.user import register_user, login

app = Sanic(__name__)

# Route the user registration API
app.add_route(login, '/login/', methods=['POST'])
app.add_route(register_user, '/register/', methods=['POST'])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
