from fastapi.testclient import TestClient
from starlette.responses import Response

client = TestClient(app)

def test_user_login():
    username = "stephenbaione"
    password = "zThG$a$&75"
    response = client.post("/user/auth/login", data={"username": username, 'password': password})
    assert response.status_code == 200
