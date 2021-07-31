# TASKS FOR DOWNLOADING ENTER USER LIBRARY

from typing import Any
from datetime import datetime

import httpx

from core.security.auth import user_auth as UserAuth

from external_services.spotify import oauth2
from external_services.spotify.internal import auth as SpotifyAuth
from external_services.spotify.services import spotify_service as SpotifyService
from external_services.spotify.models.spotify import TopTrackObject, TrackObject

from celery_queue.service.celery_service import celeryApp


BASE_URL = "https://api.spotify.com/v1/me"

async def initialize_spotify_user():
    pass

def get_timestamp(now: datetime = None):
    if now:
        return int(datetime.timestamp(now)) * 1000
    return int(datetime.timestamp(datetime.now())) * 1000

async def fetch_users_recently_played_tracks(access_token, limit = 50, before_ms: datetime = None, after_ms: datetime = None):
    if before_ms and after_ms:
        raise Exception("before_ms xor after_ms")

    user = await UserAuth.get_current_user(access_token)
    endpoint = "/player/recently-played"

    header = {
        'Authorization': f"Bearer {user['keychain']['spotify']['access_token']}"
    }

    now = get_timestamp(datetime.utcnow())
    cursor = {
        'key': 'before',
        'value': now
    }
    track_objects = await collect_batch_tracks(endpoint, user, cursor, **{'header': header,
    'cursor_size': 50,
    'params': {'limit': 50, 'before': get_timestamp(datetime.utcnow())}
    })

    return track_objects

async def format_spotify_tracks(resp, user):
    track_objects = []

    tracks = resp.json()['items']
    for track in tracks:
        track: dict = track['track']
        track.setdefault('restrictions', [])
        track.setdefault('external_ids', {})
        track.setdefault('external_urls', {})
        track.setdefault('is_playable', True)
        
        # Prepare added field
        track['visited_users'] = [str(user['_id'])]
        track['total_visited'] = 1;

        # Prepare received data
        track['album_id'] = track['album']['id']
        track['images'] = track['album']['images']

        track.pop("album")

        formattedArtistIds = []
        artist_names = []
        for artist in track['artists']:
            formattedArtistIds.append(artist['id']);
            artist_names.append(artist['name'])
        
        track['artist_ids'] = formattedArtistIds
        track['artist_names'] = artist_names
        track.pop('artists')

        # Create Top Object
        from datetime import datetime
        top_track = TopTrackObject(**{
            'user_id': str(user['_id']),
            'timestamp': datetime.utcnow(),
            "track_id": track['id'],
            "type": "top-track"
        })

        # Store Track
        track = TrackObject(**track)
        await SpotifyService.store_track(track)
        track_objects.append(dict(track))

        # Store Top Object
        await SpotifyService.store_top_track(top_track)

    return track_objects

async def collect_batch_tracks(endpoint: str, user, cursor, **options):
    '''
    Limit, after, before
    after xor before: timestamps (utc)

    '''
    cursor_size = options.get("cursor_size", None)
    header = options.get('header', None)
    params: dict = options.get('params', None)
    params = '&'.join([f"{key}=" + str(value) for (key, value) in params.items() if params])

    formatted_endpoint = f"{endpoint}?{params}"
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get(formatted_endpoint, headers=header if header else None)
        
        if resp.status_code != 200:
            return resp

        track_history = resp.json()['items']
        track_objects = await format_spotify_tracks(resp, user)

        if len(track_objects) >= cursor_size:
            last_timestamp = datetime.strptime(track_history[-1]['played_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            last_timestamp = get_timestamp(last_timestamp)

            cursor['value'] = last_timestamp
            options['params']['before'] = last_timestamp

            return track_objects + await collect_batch_tracks(endpoint, user, cursor, **options)
        return track_objects


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
    