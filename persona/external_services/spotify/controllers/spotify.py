import httpx

from datetime import date, datetime, timedelta

from requests.api import head

from external_services.spotify import oauth2

from core.data.models.auth.token import Token

BASE_URL = "https://api.spotify.com/v1/me"

class SpotifyController():

    # USER PROFILE
    def __init__(self, token: Token = None) -> None:
        self.token = token

    '''def _token_validation(f):
        import functools
        @functools.wraps(f)
        async def check_token_validation(*args, **kwargs):
            expiration = datetime.utcnow() + timedelta(seconds=self.token['expires_in'])
            now = datetime.utcnow()
            if expiration <= now:
                return False
            return True'''

    async def check_token_validation(self):
        expiration = datetime.utcnow() + timedelta(self.token['expires_in'])
        now = datetime.utcnow()
        if expiration <= now:
            return False
        return True

    # @_token_validation
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

    # LIBRARY
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
