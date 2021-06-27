from core.security.auth import user_auth
from core.data.db import db

async def handle_user_auth(username, password):
    success, user = await db.get_user_by_field("username", username)
    if not success:
        return None
    password_hash = user["password_hash"]
    result = await user_auth.authenticate_user(password, password_hash)
    if result:
        user["_id"] = str(user["_id"])
        token = await user_auth.create_access_token(user)
        return token
    return None

async def handle_user_route_validation(token, category):
    # Check if authentication token is valid
    # Check if user has privelages for route
    # TODO:// Make some kind of cfg file for this
    credentials = {
        "user_crud": ["admin"]
    }
    
