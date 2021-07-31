import httpx

from datetime import date, datetime, timedelta

from requests.api import head

from external_services.spotify import oauth2

from core.data.models.auth.token import Token

BASE_URL = "https://api.spotify.com/v1/me"

async def check_token_validation(token: Token):
    expiration = datetime.utcnow() + timedelta(token['expires_in'])
    now = datetime.utcnow()
    if expiration <= now:
        return False
    return True

async def get_user_profile_data(access_token: str):

    endpoint = "/"
    header = {
        "Authorization":
        f"Bearer {access_token}"
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