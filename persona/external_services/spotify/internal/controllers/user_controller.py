from external_services.spotify.models.user import User
import celery
from core.security.auth import user_auth
import functools

from core.data.services.user import user as UserService
from core.security.auth import user_auth as UserAuth

from external_services.spotify.services import spotify_service as SpotifyService
from external_services.spotify.internal import auth as SpotifyAuth
from external_services.spotify.internal.api import auth as AuthAPI

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
        
        result = await SpotifyAuth.refresh_token(user['_id'])
        if result is not None:
            spotify_token = result
        
        return await func(*args, **kwargs)
    return wrapper


@validate_credentials
async def get_user_profile_data(access_token: str):
    user = await UserAuth.get_current_user(access_token)
    
    persona_id = str(user["_id"])
    spotify_user = await SpotifyService.get_user_by_persona_id(persona_id)

    # User exists
    if spotify_user:
        return spotify_user

    # Create User Profile
    spotify_token = user['keychain']['spotify']
    spotify_user = await AuthAPI.get_user_profile_data(spotify_token['access_token'])
    spotify_user['user_id'] = spotify_user['id']
    spotify_user.pop('id')
    spotify_user['persona_id'] = persona_id
    spotify_user = User(**spotify_user)
    spotify_user = await SpotifyService.add_user(spotify_user)
    if spotify_user:
        return spotify_user
    return None
    
    

