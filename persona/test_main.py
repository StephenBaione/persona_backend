import http
from fastapi.exceptions import HTTPException
from fastapi.security import base
from starlette import responses

from fastapi.testclient import TestClient

from datetime import datetime

from main import app

from core.data.models.auth.token import Token

import argparse

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str)

args = parser.parse_args()

mode = args.mode

if mode == "unit":
    print(mode)

    def test_user_login():
        endpoint = "/user/auth/login"
        username = "mrrobot"
        password = "Persona123!!"

        body = {
            "username": username,
            "password": password
        }

        response = client.post(endpoint, json=body)
        assert response.status_code == 200

        resp_json: dict = response.json()
        print(resp_json)

        keys = [
            "access_token",
            "refresh_token",
            "token_type",
            "scope",
            "expires_in"
        ]

        for key in keys:
            value = resp_json.get(key)
            print(f"Key = {key}\nValue = {value}\n")
            assert(value is not None)
    client = TestClient(app)
    test_user_login()

else:
    class DevTestClient:
        def __init__(self, token = None) -> None:
            self.token = token
        
        def login_user(self, username, password):
            endpoint = "/user/auth/login"

            body = {
                "username": username,
                "password": password
            }

            with httpx.Client(base_url="http://127.0.0.1:8000") as client:
                resp = client.post(endpoint, json=body)
                if resp.status_code == 200:
                    print("Success logging in.")
                    token = Token(**resp.json())
                    self.token = token
                else:
                    raise HTTPException(status_code=resp.status_code, detail=resp.text)

        def login_user(self, username, password):
            endpoint = "/user/auth/login"

            body = {
                "username": username,
                "password": password
            }

            with httpx.Client(base_url="http://127.0.0.1:8000") as client:
                resp = client.post(endpoint, json=body)
                if resp.status_code == 200:
                    print("Success logging in.")
                    token = Token(**resp.json())
                    self.token = token
                else:
                    raise HTTPException(status_code=resp.status_code, detail=resp.text)
                
    def main_loop():

        while True:
            client = DevTestClient()
            arg = input("---- Input Argument ----\n")
            if arg == 'Q':
                exit(0)
            if arg == "login":
                username = input("Username: ")
                password = input("Password: ")
                client.login_user(username, password)
            else:
                exit(1)
    main_loop()
