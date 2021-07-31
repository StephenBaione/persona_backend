from copy import Error
from time import sleep

from pydantic.networks import HttpUrl
from core.data.models.utils.temporary import TemporaryModel
import uuid

from pydantic.types import UUID5
from core.security.auth import user_auth
import webbrowser

from typing import Optional
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Cookie
from starlette.responses import Response

from core.data.models.user.model import User
from core.data.models.auth.token import Token

from core.tasks import spotify as SpotifyTasks

from core.data.services.user import user as UserService
from core.data.services.utils import temporaryService

from external_services.spotify.services import spotify_service as SpotifyService

from celery.result import AsyncResult

from fastapi import BackgroundTasks


from external_services.spotify import oauth2
from external_services.spotify.internal.controllers import auth_controller as AuthController

router = APIRouter(prefix="/spotify/auth", tags=["spotify"])

SCOPE = [
    # Images
    "ugc-image-upload",
    # Listening History
    "user-read-recently-played",
    "user-top-read",
    "user-read-playback-position",
    # Spotify Connect
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    # Playback
    "app-remote-control",
    "streaming",
    # Playlists
    "playlist-modify-public",
    "playlist-modify-private",
    "playlist-read-private",
    "playlist-read-collaborative",
    # Follow
    "user-follow-modify",
    "user-follow-read",
    # Library
    "user-library-modify",
    "user-library-read",
    # Users
    "user-read-email",
    "user-read-private"
]


@router.get("/authorization", response_model=dict, response_description="initialize oauth2 flow")
async def initialize_oauth2_flow(access_token: str):
    # response.set_cookie('_id', user_id)
    # state = str(uuid.uuid4())
    # url = await oauth2.request_authorization(state=state, scope=SCOPE).url

    result = await AuthController.initialize_oauth2_flow(access_token)
    response = result[0]
    state = result[1]
    status = 200
    if response == None:
        status = 404
    if response.status_code != 200:
        return HTTPException(status, response.text)

    return {
        "Redirect": str(response.url),
        "State": state
    }

@router.get("/redirect", response_description="Spotifty token redirect")
async def oauth2_flow_redirect(code: str, state: str, error: Optional[str] = None, _id: Optional[str] = Cookie(None)):
    if error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    success = await AuthController.oauth2_flow_redirect(code, state)
    return {
        "success": str(success)
    }

@router.get("/result/status", response_description="Status of authentication process")
async def oauth_result_status(access_token: str, state: str):
    status = await AuthController.oauth_result_status(access_token, state)
    return {
        "status": status
    }

@router.get("/result", response_description="Result of authentication process")
async def oauth2_result(_id: str, state: str, background_tasks: BackgroundTasks):

    # Get temporary object from storage
    async def func(_id, state):
        checkpoint: TemporaryModel = await temporaryService.get_temporary_object(state)
        token = checkpoint['data']
        user = await UserService.get_user(_id)
        if user is None:
            return HTTPException(404, "User Not Found...")
        
        await UserService.add_to_user_keychain(_id, "spotify", token)
    background_tasks.add_task(func, _id, state)
    return {}
    
@router.post("/refresh", response_description="Spotify token refresh")
async def oauth2_flow_refresh(token: Token):
    token = jsonable_encoder(token)
    new_token = await oauth2.request_refresh_token(token)
    return {
        "token": new_token
    }
