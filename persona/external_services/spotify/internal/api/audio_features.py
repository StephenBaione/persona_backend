import httpx

from external_services.spotify.services import spotify_service as SpotifyService

from core.data.services.user import user as UserService

async def get_audio_features_batch(_id, track_ids: list):
    if len(track_ids) > 100:
        return None

    user = await UserService.get_user(_id)
    spotify_token = user['keychain'].get('spotify', None)
    
    base = "https://api.spotify.com/v1"
    endpoint = "/audio-features"
    track_ids = ','.join(track_ids)
    endpoint += f"?ids={track_ids}"
    headers = {
        'Authorization': f"Bearer {spotify_token['access_token']}"
    }
    async with httpx.AsyncClient(base_url=base) as client:
        resp = await client.get(endpoint, headers = headers)
        return resp.json()

