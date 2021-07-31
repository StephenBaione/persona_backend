from core.data.models.utils.temporary import TemporaryModel
from core.data.db.db import temporary_collection

async def store_temporary_object(temp: dict):
    data = await temporary_collection.insert_one(temp)
    new_data = await temporary_collection.find_one({"uuid": temp["uuid"]})
    if new_data is None:
        return None
    return new_data

async def get_temporary_object(uuid: str):
    data =  await temporary_collection.find_one({"uuid": uuid})
    return data
    
