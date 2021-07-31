from core.data.models.utils.temporary import TemporaryModel
from core.security.auth import user_auth as UserAuth
from core.data.models.auth.token import Token
from external_services.spotify.internal import auth
import uuid

import functools

from external_services.spotify import oauth2

from celery.result import AsyncResult

from core.data.services.user import user as UserService
from core.data.services.utils import temporaryService as TemporaryService

from core.tasks import spotify as SpotifyTasks

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

def validate_user_token(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        user = await UserAuth.get_current_user(args[0])
        if user is None:
            return None
        # spotify_token = user['keychain']['spotify']
        # expired = await auth.check_token_validation(spotify_token)
        # if expired:
        #     spotify_token = auth.refresh_token(user['_id'])
        return await func(*args, **kwargs)
    return wrapper

def validate_credentials(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Validate user credentials
        user = await UserAuth.get_current_user(args[0])
        if user is None:
            return None

        # Validate or refresh spotify token
        spotify_token = user['keychain'].get('spotify', None)
        if spotify_token is None:
            return None
        
        result = await auth.refresh_token(user['_id'])
        if result is not None:
            spotify_token = result
        
        return await func(access_token=spotify_token['access_token'], *args, **kwargs)

@validate_user_token
async def initialize_oauth2_flow(access_token):

    state = str(uuid.uuid4())
    response = await oauth2.request_authorization(state=state, scope=SCOPE)
    return (response, state)

async def oauth2_flow_redirect(code: str, state: str) -> bool:
    # Create Checkpoint for tracking token status
    token = await oauth2.request_access_token(code)
    checkpoint = TemporaryModel(** {
        'uuid': state,
        'tag': 'spotify',
        'data': token
    })
    await SpotifyTasks.create_auth_checkpoint(checkpoint)
    return True

@validate_user_token
async def oauth_result_status(access_token: str, state: str):
    resp = AsyncResult(f"spotify-auth-{state}")
    return resp.status

    
