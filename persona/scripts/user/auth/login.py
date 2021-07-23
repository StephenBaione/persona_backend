import os
import requests
import httpx
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--username", type=str)
parser.add_argument("--password", type=str)

args = parser.parse_args()

BASE_URL = "http://127.0.0.1:8000/user/auth"

path = "/login"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

data = {
    "username": args.username,
    "password": args.password
}

print(data)

async def login_user(username = args.username, password = args.password):
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        resp = await client.post(url=path, headers=headers, data=data)
        if resp.status_code == 200:
            print("Success")
        print("Failure")


