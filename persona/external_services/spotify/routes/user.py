from external_services.spotify.internal import auth
import json
from external_services.spotify.models.spotify import ArtistObject, AudioFeaturesObject, TrackObject, SavedAlbumObject, SavedTrackObject, AlbumObject, TopTrackObject
from jose import jwt
from kombu.exceptions import HttpError
from core.security.auth import user_auth
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, security, status
from fastapi.encoders import jsonable_encoder
import httpx
from requests.models import encode_multipart_formdata

from external_services.spotify import oauth2
from external_services.spotify.controllers.spotify import SpotifyController
from external_services.spotify.models.user import User
from external_services.spotify.services import spotify_service as SpotifyService
from external_services.spotify.internal.api import audio_features as AudioFeaturesAPI
from external_services.spotify.internal.tasks import library as LibraryTask

from external_services.spotify.internal.controllers import user_controller as UserController

from core.data.models.auth.token import Token

from core.data.services.user import user as UserService

from core.security.auth import user_auth as UserAuth

CONFIG = oauth2.config

BASE_URL = "https://api.spotify.com/v1/me"

_SPOTIFY_CONTROLLER = SpotifyController()


router = APIRouter(prefix="/spotify/auth", tags=["spotify/me"])

@router.get("/user", response_description="Get user profile data")
async def get_user_profile_data(access_token: str):
    data = await UserController.get_user_profile_data(access_token)
    return data

# TODO:// Move heavy logic and create Task for saving albums
@router.get("/user/saved_albums", response_description="Get user saved albums")
async def get_user_saved_albums(access_token: str):
    # Authorize request
    user = await UserAuth.get_current_user(access_token=access_token)
    
    spotify_token = user['keychain'].get('spotify', None)
    if not spotify_token:
        return HttpError(401)
    
    spotify_access_token = spotify_token['access_token']
    
    # send get request to endpoint
    endpoint ="/albums"
    header = {
        "Authorization": 
        f"Bearer {spotify_access_token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get(endpoint, headers=header)
        if resp.status_code != 200:
            raise HTTPException(
                resp.status_code,
                detail=f"Status Code: {resp.status_code}\nReason: {resp.reason_phrase}")
        
        # Iterate through album objects and save
        items = resp.json()['items']
        for (index, item) in enumerate(items):
            album: dict = item['album']

            # Prepare added fields in album object
            item['album_id'] = album['id']
            item['user_id'] = str(user['_id'])
            from datetime import datetime
            
            # Convert timestamp to datetime
            # Received Format: 'YYYY-MM-DDTHH:MM:SSZ'
            item['added_at'] = datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ')

            # Save Object
            item.pop("album")
            saved_album_object = SavedAlbumObject(**item);
            result = await SpotifyService.store_saved_albums_object(saved_album_object)
            
            # Prepare added field
            album['visited_users'] = [str(user['_id'])]
            album['total_visited'] = 1;

            # TODO:// Fix this for optional fields
            album.setdefault('restrictions', None)

            # Save object
            # Prepare received data
            formattedTracks = []
            tracks = album['tracks']['items']
            for track in tracks:
                formattedTracks.append(track['id'])
            album['tracks'] = formattedTracks

            album = AlbumObject(**album)
            await SpotifyService.store_album(album)

        return resp.json()

@router.get("/user/top_artists", response_description="Get user top artists")
async def get_user_top_artists(access_token: str):
    # Authorize request
    user = await UserAuth.get_current_user(access_token=access_token)
    
    spotify_token = user['keychain'].get('spotify', None)
    if not spotify_token:
        return HttpError(401)
    
    spotify_access_token = spotify_token['access_token']
    
    # send get request to endpoint
    endpoint ="/top/artists"
    header = {
        "Authorization": 
        f"Bearer {spotify_access_token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get(endpoint, headers=header)
        if resp.status_code != 200:
            raise HTTPException(
                resp.status_code,
                detail=f"Status Code: {resp.status_code}\nReason: {resp.reason_phrase}")
        # Iterate through artist objects and save
        artists = resp.json()['items']
        artist_objects = []
        for artist in artists:
            artist: ArtistObject = artist
            res = await SpotifyService.store_artist_object(artist)
            artist_objects.append(artist)
            
        return artist_objects

            
        '''# Iterate through album objects and save
        items = resp.json()['items']
        print(len(items))
        for (index, item) in enumerate(items):
            print(index)
            album: dict = item['album']

            # Prepare added fields in album object
            item['album_id'] = album['id']
            item['user_id'] = str(user['_id'])
            from datetime import datetime
            
            # Convert timestamp to datetime
            # Received Format: 'YYYY-MM-DDTHH:MM:SSZ'
            item['added_at'] = datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ')

            # Save Object
            item.pop("album")
            print("\n\n-------- Item Data --------", item, "\n\n")
            saved_album_object = SavedAlbumObject(**item);
            result = await SpotifyService.store_saved_albums_object(saved_album_object)
            if result is None:
                print("\n\n-------- Already Saved... --------", item, "\n\n")
            
            # Prepare added field
            album['visited_users'] = [str(user['_id'])]
            album['total_visited'] = 1;

            # TODO:// Fix this for optional fields
            album.setdefault('restrictions', None)

            # Save object
            # Prepare received data
            formattedTracks = []
            tracks = album['tracks']['items']
            for track in tracks:
                formattedTracks.append(track['id'])
            album['tracks'] = formattedTracks

            album = AlbumObject(**album)
            await SpotifyService.store_album(album)'''

        return resp.json()

@router.get("/user/saved_tracks", response_description="Get user saved albums")
async def get_user_saved_tracks(access_token: str):
    # Authorize request
    user = await UserAuth.get_current_user(access_token=access_token)
    
    spotify_token = user['keychain'].get('spotify', None)
    if not spotify_token:
        return HttpError(401)
    
    spotify_access_token = spotify_token['access_token']
    
    # send get request to endpoint
    endpoint ="/tracks"
    header = {
        "Authorization": 
        f"Bearer {spotify_access_token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get(endpoint, headers=header)
        if resp.status_code != 200:
            raise HTTPException(
                resp.status_code,
                detail=f"Status Code: {resp.status_code}\nReason: {resp.text}")

        items = resp.json()['items']
        for item in items:
            track: dict = item['track']
            track.setdefault('restrictions', [])
            track.setdefault('external_ids', {})
            track.setdefault('external_urls', {})
            track.setdefault('is_playable', True)

            # Prepare added fields in album object
            item['track_id'] = track['id']
            item['user_id'] = str(user['_id'])
            
            # Convert timestamp to datetime
            # Received Format: 'YYYY-MM-DDTHH:MM:SSZ'
            from datetime import datetime
            item['added_at'] = datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ')

            # Save Object
            item.pop("track")
            saved_album_object = SavedTrackObject(**item);
            await SpotifyService.store_saved_tracks_object(saved_album_object)
            
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
                formattedArtistIds.append(artist['id'])
                artist_names.append(artist['name'])
            
            track['artist_ids'] = formattedArtistIds
            track['artist_names'] = artist_names
            track.pop('artists')

            track = TrackObject(**track)
            await SpotifyService.store_track(track)

        return resp.json()

@router.get("/user/top_tracks", response_description="Get user Top Tracks")
async def get_user_top_tracks(access_token: str):
    # Authorize request
    user = await UserAuth.get_current_user(access_token=access_token)
    
    spotify_token = user['keychain'].get('spotify', None)
    if spotify_token is None:
        return HttpError(401, message="Fuck nah...")
    
    spotify_access_token = spotify_token['access_token']
    
    # send get request to endpoint
    endpoint ="/top/tracks"
    header = {
        "Authorization": 
        f"Bearer {spotify_access_token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.get(endpoint, headers=header)
        if resp.status_code != 200:
            raise HTTPException(
                resp.status_code,
                detail=f"Status Code: {resp.status_code}\nReason: {resp.reason_phrase}")

        track_objects = []

        tracks = resp.json()['items']
        for track in tracks:
            track: dict = track
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

        return {
            'tracks': track_objects
        }


@router.get("/user/top_audio_features", response_description="Get user Top Track Audio Features")
async def get_user_top_track_features(access_token: str):
    user = await UserAuth.get_current_user(access_token)
    if user is None:
        raise HttpError(401, message="Invalid access token")
    top_tracks = await SpotifyService.retreive_users_top_tracks(str(user['_id']))
    print(top_tracks)
    track_ids = []
    for top_track in top_tracks:
        track_ids.append(top_track['track_id'])
    audio_features = await AudioFeaturesAPI.get_audio_features_batch(str(user['_id']), track_ids)
    audio_features_objects = []
    for audio_feature in audio_features['audio_features']:
        audio_feature['track_id'] = audio_feature['id']
        audio_feature.pop('id')
        audio_feature = AudioFeaturesObject(**audio_feature)
        await SpotifyService.store_audio_feature(audio_feature)
        audio_features_objects.append(audio_feature)
    return {
        "audio_features": audio_features_objects
    }
    
    
@router.get("/user/recently_played", response_description="Get Spotify's recently played tracks")
async def get_user_recently_played(access_token: str):
    results = await LibraryTask.fetch_users_recently_played_tracks(access_token)
    return {'fetching': results}
