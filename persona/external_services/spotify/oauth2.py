from os import register_at_fork
import httpx

import base64

from core.data.models.auth.token import Token
# Check if user has spotify token in keychain
# Have Token:
#   Check if token is valid
#   if not, perform token refresh
# Not Have Token:
#   Perform full authorization flow

config = {
    "CLIENT_ID": "3656a63cf4f547fd9c03f80a208c2e31",
    "CLIENT_SECRET": "dbcfa2b2a2a242d0b675417adceb6c57",
    "RESPONSE_TYPE": "code",
    "REDIRECT_URI": "http://127.0.0.1:8000/spotify/auth/redirect",
    "GRANT_TYPE": "authorization_code",
    "GRANT_TYPE_REFRESH": "refresh_token"
}

BASE_ACCOUNTS_SERVICE = "https://accounts.spotify.com"

async def format_auth_header(client_id: str, client_secret: str):
    encoded_client_credentials = base64.b64encode(bytes(f"{client_id}:{client_secret}", 'ascii'))
    return f"Basic {encoded_client_credentials.decode('ascii')}"


async def request_authorization(state: str = None, scope: list = None):
    endpoint = "/authorize"
    params = {
        "client_id": config["CLIENT_ID"],
        "response_type": config["RESPONSE_TYPE"],
        "redirect_uri": config["REDIRECT_URI"]
    }
    if state:
        params["state"] = state
    if scope:
        params["scope"] = ' '.join(scope)
    async with httpx.AsyncClient(base_url=BASE_ACCOUNTS_SERVICE) as client:
        resp = await client.get(endpoint, params=params)
        if resp.status_code != 200:
            raise Exception(f"Error requesting spotify authorization\n{resp.reason_phrase}")
        return resp.url


async def request_access_token(code: str):
    endpoint = "/api/token"
    body = {
        "grant_type": config["GRANT_TYPE"],
        "code": code,
        "redirect_uri": config["REDIRECT_URI"]
    }
    encoded_client_credentials = base64.b64encode(bytes(f"{config['CLIENT_ID']}:{config['CLIENT_SECRET']}", 'ascii'))
    auth_header = {"Authorization": f"Basic {encoded_client_credentials.decode('ascii')}"}
    async with httpx.AsyncClient(base_url=BASE_ACCOUNTS_SERVICE) as client:
        resp = await client.post(endpoint, data=body, headers=auth_header)
        if not resp.status_code == 200:
            raise Exception("Error in retrieving user token")
        return Token(**resp.json())

async def request_refresh_token(token: Token):
    endpoint = "/api/token"
    body = {
        "grant_type": config["GRANT_TYPE_REFRESH"],
        "refresh_token": token["refresh_token"]
    }
    auth_header = await format_auth_header(config["CLIENT_ID"], config["CLIENT_SECRET"])
    async with httpx.AsyncClient(base_url=BASE_ACCOUNTS_SERVICE) as client:
        resp = await client.post(endpoint, data=body, headers={"Authorization": auth_header})
        if resp.status_code != 200:
            raise Exception("Error refreshing token")
        return Token(**resp.json())

