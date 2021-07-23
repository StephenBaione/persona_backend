from os import access
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
import httpx
from requests.models import encode_multipart_formdata

from external_services.spotify import oauth2
from external_services.spotify.controllers.spotify import SpotifyController


from core.data.models.auth.token import Token

CONFIG = oauth2.config

BASE_URL = "https://api.spotify.com/v1/me"

_SPOTIFY_CONTROLLER = SpotifyController()

router = APIRouter(prefix="/spotify/auth", tags=["spotify/me"])

@router.get("/user", response_description="Get user profile data")
async def get_user_profile_data(access_token: str):
    # Format header for Authorization
    # send get request to endpoint
    endpoint ="/"
    header = {
        "Authorization": 
        f"Bearer {access_token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get(endpoint, headers=header)
        if resp.status_code != 200:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"Status Code: {resp.status_code}\nReadon: {resp.reason_phrase}")
        return resp.json()

@router.get("/user/saved_albums", response_description="Get user saved albums")
async def get_user_saved_albums(access_token: str):
    data = await _SPOTIFY_CONTROLLER.get_user_saved_albums(access_token)
    if data is None:
        return {"message": "Error retrieving saved albums"}
    return data

    


