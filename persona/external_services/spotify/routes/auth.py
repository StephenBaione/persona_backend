import webbrowser

from typing import Optional
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder

from core.data.models.user.model import User
from core.data.models.auth.token import Token

from external_services.spotify import oauth2

router = APIRouter(prefix="/spotify/auth", tags=["spotify"])

@router.get("/authorization", response_description="initialize oauth2 flow")
async def initialize_oauth2_flow(user_id: str):
    url = await oauth2.request_authorization(scope=["user-read-private", "user-read-email", "user-library-read", "user-library-modify"])
    # TODO:// Setup debug configuration. Line is only for testing.
    webbrowser.open(str(url))
    print(url)
    return {
        "message": f"Redirect to {url}"
    }

@router.get("/redirect", response_description="Spotifty token redirect")
async def oauth2_flow_redirect(code: str, state: Optional[str] = None, error: Optional[str] = None):
    if error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    token = await oauth2.request_access_token(code)
    return {
        "token": token
    }
    
@router.post("/refresh", response_description="Spotify token refresh")
async def oauth2_flow_refresh(token: Token):
    token = jsonable_encoder(token)
    new_token = await oauth2.request_refresh_token(token)
    return {
        "token": new_token
    }
