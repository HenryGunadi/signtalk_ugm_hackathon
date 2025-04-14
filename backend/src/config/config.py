from flask import Flask

def init_config(app: Flask, secret_key: str, jwt_cookie_secure: str) -> None:
    # config
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_SECRET_KEY"] = secret_key if secret_key else "development-key"
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"

    app.config["JWT_COOKIE_CSRF_PROTECT"] = True  
    app.config["JWT_COOKIE_SECURE"] = True if jwt_cookie_secure == "True" else False  # Set to True in production (HTTPS only)