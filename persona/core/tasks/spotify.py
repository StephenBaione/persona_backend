from os import name
from core.data.models.utils.temporary import TemporaryModel
from core.data.models.auth.token import Token
from core.data.services.utils import temporaryService

from external_services.spotify.models.spotify import TrackObject

import celery

import uuid


async def initSpotify(token: Token):
    pass

class CreateCheckpointTask(celery.Task):
    def __init__(self, type, checkpoint: TemporaryModel) -> None:
        super().__init__()
        self.name = f"spotify-{type}-{checkpoint['uuid']}"
        self.checkpoint = checkpoint
    
    async def __call__(self, *args, **kwargs):
        result = await temporaryService.store_temporary_object(self.checkpoint)
        return result

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))

async def create_auth_checkpoint(checkpoint: TemporaryModel):
    checkpoint_data = {
        "uuid": checkpoint.uuid,
        "tag": checkpoint.tag,
        "data": checkpoint.get_data()
    }
    task = CreateCheckpointTask("auth", checkpoint_data)
    print("Starting Task...")
    await task()

class MineTrackFeatures(celery.Task):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)



class CalculateBaseTrackStatistics(celery.Task):
    def __init__(self, tracks: list) -> None:
        super().__init__()
        self.name = f"spotify-tracks-{str(uuid.uuid4())}"
        self.tracks = tracks

    async def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        
        statistics = {}
        
    
