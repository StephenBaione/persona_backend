from array import ArrayType
from pydantic import BaseModel, Field

from typing import Optional, Any

from datetime import datetime


# ---- ALBUM OBJECT ----
class SavedAlbumObject(BaseModel):
    user_id: str = Field(...)

    added_at: datetime = Field(...)
    album_id: str = Field(...)

class AlbumObject(BaseModel):
    # Added Fields
    visited_users: list = Field(...)
    total_visited: int = Field(...)

    # Spotify Fields
    id: str = Field(...)
    album_type: str = Field(...)
    artists: list = Field(...)
    available_markets: list = Field(...)
    copyrights: list = Field(...)
    external_ids: Any = Field(...)
    external_urls: Any = Field(...)
    genres: list = Field(...)
    href: str = Field(...)
    images: list = Field(...)
    label: str = Field(...)
    name: str = Field(...)
    popularity: int = Field(...)
    release_date: str = Field(...)
    release_date_precision: str = Field(...)
    restrictions: Optional[Any] = Field(...)
    total_tracks: int = Field(...)
    tracks: list = Field(...)
    type: str = Field(...)
    uri: str = Field(...)

# TRACK OBJECTS
class SavedTrackObject(BaseModel):
    # Added fields
    user_id: str = Field(...)

    # Spotify fields
    added_at: datetime = Field(...)
    track_id: str = Field(...)

class TrackObject(BaseModel):
    # Added Fields
    visited_users: list = Field(...)
    total_visited: int = Field(...)

    images: list = Field(...)
    artist_names: list = Field(...)

    # Spotify Fields
    id: str = Field(...)
    album_id: str = Field(...)
    artist_ids: list = Field(...)
    available_markets: list = Field(...)
    disc_number: int = Field(...)
    duration_ms: int = Field(...)
    explicit: bool = Field(...)
    external_ids: dict = Field(...)
    external_urls: dict = Field(...)
    href: str = Field(...)
    is_local: bool = Field(...)
    is_playable: bool = Field(...)
    name: str = Field(...)
    popularity: int = Field(...)
    preview_url: Optional[str] = None
    restrictions: list = Field(...)
    track_number: int = Field(...)
    type: str = Field(...)
    uri: str = Field(...)

class TopTrackObject(BaseModel):
    # Added Fields
    user_id: str = Field(...)
    timestamp: datetime = Field(...)
    track_id: str = Field(...)
    type: str = Field(...)

class AudioFeaturesObject(BaseModel):
    track_id: str = Field(...)

    acousticness: float = Field(...)
    analysis_url: str = Field(...)
    danceability: float = Field(...)
    duration_ms: int = Field(...)
    energy: float = Field(...)
    instrumentalness: float = Field(...)
    key: int = Field(...)
    liveness: float = Field(...)
    loudness: float = Field(...)
    mode: int = Field(...)
    speechiness: float = Field(...)
    tempo: float = Field(...)
    time_signature: int = Field(...)
    track_href: str = Field(...)
    type: str = Field(...)
    uri: str = Field(...)
    valence: float = Field(...)

# ARTIST OBJECT 
class ArtistObject(BaseModel):
    id: str = Field(...)
    external_urls: dict = Field(...)
    followers: dict = Field(...)
    genres: list = Field(...)
    images: list = Field(...)
    name: str = Field(...)
    popularity: int = Field(...)
    type: str = Field(...)
    uri: str = Field(...)



