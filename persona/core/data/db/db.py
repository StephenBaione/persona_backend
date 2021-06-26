from bson.objectid import ObjectId
from motor import motor_asyncio

MONGO_URL = "mongodb://127.0.0.1:27017"

client = motor_asyncio.AsyncIOMotorClient(MONGO_URL)

database = client.user

user_collection = database.get_collection("user_collection")

def user_helper(user) -> dict:
    return {
        "id": user["_id"],
        "firstname": user["firstname"],
        "lastname": user["lastname"],
        "username": user["username"],
        "email": user["email"],
        "age": user["age"]
    }

async def retrieve_users():
    users = []
    async for user in user_collection.find():
        users.append(user)
    return users

# TODO:// Update service.routes.user.py so that it checks for null.
# Just return data as opposed to list object
async def get_user(user_id: dict):
    test_user = await user_collection.find_one({"firstname": "test"})
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    print(user)
    if user is None:
        raise Exception(f"Error in getting user with Id={user_id}")
    return [True, user]

async def add_user(user_data: dict) -> dict:
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"firstname": user_data["firstname"]})
    if new_user is None:
        raise Exception(f"Error in adding user with data={user_data}")
    return [True, new_user]

async def update_user(user_data: dict) -> dict:
    # TODO:// Research motor to find a better way to do this
    def check_user(old_data: dict, new_data: dict):
        for (key, val) in old_data.items():
            if val != new_data[key]:
                return False
        return True
    old_data = await user_collection.find_one({"firstname": user_data["firstname"]})
    user = await user_collection.replace_one({"_id": old_data["_id"]}, user_data)
    new_data = await user_collection.find_one({"firstname": user_data["firstname"]})
    if not check_user(old_data, new_data):
        raise Exception(f"Unable to update user {old_data}")
    return [True, new_data]
