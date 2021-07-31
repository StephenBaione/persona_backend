from binascii import Error
import httpx

from datetime import date, datetime, timedelta
from motor.frameworks.asyncio import add_future

from requests.api import head

from external_services.spotify import oauth2

from core.data.models.auth.token import Token
from core.data.services.user import user as UserService

from external_services.spotify.models.user import User
from external_services.spotify.services import spotify_service
from external_services.spotify.internal.api import auth

BASE_URL = "https://api.spotify.com/v1/me"

async def initiate_spotify_profile(token: Token):
    user_profile = await auth.get_user_profile_data(token["access_token"])
    user = User(**user_profile)
    new_user = await spotify_service.add_user(user)
    user_saved_albums = await auth.get_user_saved_albums(token["access_token"])


async def check_token_expired(token: Token):
        expiration = datetime.utcnow() + timedelta(token['expires_in'] / 1000)
        now = datetime.utcnow()
        if expiration <= now:
            return True
        return False

async def refresh_token(_id: str, spotify_token = None):
    user = await UserService.get_user(_id)
    if spotify_token is None:
        spotify_token = user['keychain']['spotify']

    expired = await check_token_expired(spotify_token)
    if not expired:
        return None

    spotify_token = await oauth2.request_refresh_token(spotify_token)
    spotify_token = dict(spotify_token)

    result = await UserService.update_user_keychain(_id, 'spotify', spotify_token)
    if result is None:
        raise Error("Could not update Spotify keychain")
    return spotify_token
        


async def get_user_profile_data(self, access_token: str):
        if not await self.check_token_validation():
            self.token = await oauth2.request_refresh_token(self.token)
        endpoint = "/"
        header = {
            "Authorization":
            f"Bearer: {access_token}"
        }
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            resp = await client.get(endpoint, headers=header)
            if resp.status_code != 200:
                return None
            return resp.json()

async def get_user_saved_albums(self, access_token: str, **params):
        if self.token is None:
            self.token = access_token
        if not await self.check_token_validation():
            self.token = await oauth2.request_refresh_token(self.token)
        endpoint = "/albums"
        header = {
            "Authorization":
            f"Bearer: {access_token}"
        }
        params.setdefault("limit", 50)
        params.setdefault("offset", 0)
        params.setdefault("market", "from_token")
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            resp = await client.get(endpoint, headers=header, params=params)
            if resp.status_code != 200:
                return None
            return resp.json()