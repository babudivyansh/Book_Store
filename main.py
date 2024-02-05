"""
@Author: Divyansh Babu

@Date: 2024-01-31 12:40

@Last Modified by: Divyansh Babu

@Last Modified time: 2024-02-01 12:37

@Title : Book Store app using Sanic.
"""
from sanic import Sanic
from Routes.user import app as ur
from Routes.book import app as br

app = Sanic(__name__)

app.ext.openapi.add_security_scheme(
    "authorization",
    "http",
    scheme="bearer",
    bearer_format="JWT",
)
app.config["API_SECURITY"] = [{"ApiKeyAuth": []}]
app.config["API_SECURITY_DEFINITIONS"] = {
    "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}
}

app.blueprint(ur)
app.blueprint(br)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
