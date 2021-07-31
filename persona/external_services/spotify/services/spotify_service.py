from external_services.spotify.models.spotify import AlbumObject, ArtistObject, AudioFeaturesObject, TopTrackObject, TrackObject, SavedAlbumObject, SavedTrackObject
from core.data.models.auth.token import Token

from core.data.db.db import spotify_collection

from external_services.spotify.models.user import User

from core.data.services.user import user as UserService

async def add_user(user_data: User):
    user_data = dict(user_data)
    user = await spotify_collection.insert_one(user_data)
    new_user = await spotify_collection.find_one({"user_id": user_data["user_id"]})
    new_user["_id"] = str(new_user["_id"])
    return new_user

async def get_user(user_id):
    user = await spotify_collection.find_one({'user_id': user_id})
    if user:
        user['_id'] = str(user['_id'])
        return user
    return None

async def get_user_by_persona_id(persona_id: str):
    user = await spotify_collection.find_one({"persona_id": persona_id})
    if user:
        user['_id'] = str(user['_id'])
        return user
    return None

async def store_saved_albums_object(saved_albums_object: SavedAlbumObject):
    # No duplicated
    print('Storing...')
    if await spotify_collection.find_one(dict(saved_albums_object)):
        return None

    print("Juuuuuuust about to store...", saved_albums_object)
    _object = await spotify_collection.insert_one(dict(saved_albums_object))
    return _object

async def store_album(album: AlbumObject):
    existing_album: AlbumObject = await spotify_collection.find_one(dict(album))
    album_object: AlbumObject

    # Add user to visited_users list and increment count
    if existing_album:
        existing_album = AlbumObject(**existing_album)
        existing_album.visited_users.append(album.visited_users[0])
        existing_album.total_visited += album.total_visited
        existing_album = dict(existing_album)
        album_object = await spotify_collection.replace_one({"id": existing_album['id']}, existing_album)

    # Insert new album object
    else:
        album_object = await spotify_collection.insert_one(dict(album))
    
    return album_object

async def store_saved_tracks_object(saved_tracks_object: SavedTrackObject):
    # No duplicated
    print('Storing...')
    if await spotify_collection.find_one(dict(saved_tracks_object)):
        return None

    print("Juuuuuuust about to store...", saved_tracks_object)
    _object = await spotify_collection.insert_one(dict(saved_tracks_object))
    return _object

async def store_track(track: TrackObject):
    existing_track: TrackObject = await spotify_collection.find_one(dict(track))
    track_object: TrackObject

    # Add user to visited_users list and increment count
    if existing_track:
        existing_track = TrackObject(**existing_track)
        existing_track.visited_users.append(track.visited_users[0])
        existing_track.total_visited += track.total_visited
        existing_track = dict(existing_track)
        await spotify_collection.replace_one({"id": existing_track['id']}, existing_track)
        track_object = existing_track

    # Insert new album object
    else:
        track_object = await spotify_collection.insert_one(dict(track))
    
    return track_object

async def retrieve_track(track_id: str):
    return await spotify_collection.findOne({'id': track_id})

async def retrieve_track_batch(track_ids: list):
    return await spotify_collection.find({'id': {'$in': track_ids}})

async def store_top_track(top_track: TopTrackObject):
    existing_top_track: TopTrackObject = await spotify_collection.find_one(dict(top_track))
    if existing_top_track:
        return None
    
    top_track_object = await spotify_collection.insert_one(dict(top_track))
    return top_track_object

async def retreive_users_top_tracks(_id: str):
    print(_id)
    top_tracks = await spotify_collection.find({'user_id': {"$eq": _id}, 'type': {'$eq': 'top-track'}}).to_list(100)
    return top_tracks

async def store_artist_object(artist: ArtistObject):
    existing_artist: ArtistObject = await spotify_collection.find_one(dict(artist))
    if existing_artist is not None:
        return None
    await spotify_collection.insert_one(dict(artist))

async def store_audio_feature(audio_feature: AudioFeaturesObject):
    audio_feature = dict(audio_feature)
    existing_feature: AudioFeaturesObject = await spotify_collection.find_one({'track_id': audio_feature['track_id']})
    if existing_feature is not None:
        return None
    audio_feature_object = await spotify_collection.insert_one(dict(audio_feature))
    return audio_feature_object

async def create_spotify_statistic(user: User, label, data, display_method):
    '''
    user_id: str = Field(...)
    spotify_id: str = Field(...)
    tag: str = Field(...)
    label: str = Field(...)
    data: Any = Field(...)

    display_method: str = Field(...)
    '''
    spotify_id = user.user_id
    pass


