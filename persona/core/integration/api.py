import abc
from external_services.spotify.internal.controllers.auth_controller import validate_credentials
from core.security.auth import user_auth as UserAuth
import functools
from core.security import auth
from core.integration.api_config import APIConfig

import httpx


class BaseAPI(abc.ABC):
    def __init__(self, api_config) -> None:
        super().__init__()
        self.api_config = APIConfig(**api_config)

    def validate_user_token(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            user = await UserAuth.get_current_user(args[0])
            if user is None:
                return None
            # spotify_token = user['keychain']['spotify']
            # expired = await auth.check_token_validation(spotify_token)
            # if expired:
            #     spotify_token = auth.refresh_token(user['_id'])
            return await func(*args, **kwargs)
        return wrapper

    def get_fetch_model(self, section, model_key):
        section: dict = self.api_config.url_map.get('section', None)
        if section is None:
            raise Exception(f"Invalid section for api... {self.api_config.service_name}")
        fetch_model = section.get(model_key, None)
        if fetch_model is None:
            raise Exception("Invalid model_key")
        endpoint = fetch_model['endpoint']
        params = fetch_model.get('params', None)
        headers = fetch_model.get('headers', None)
        method: str = fetch_model['method']
        body = fetch_model.get('body', None) if method.lower() == 'post' else None
        return {
            'endpoint': endpoint,
            'params': params,
            'headers': headers,
            'method': method,
            'body': body
        }

    async def fetch_endpoint(self, section, model_key):
        fetch_model = self.get_fetch_model(section, model_key)
        BASE_URL = section['BASE_URL']
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            endpoint = fetch_model['endpoint']
            method = fetch_model['method']
            if method.lower() == 'post':
                body = fetch_model.get('body', None)
            params = fetch_model.get('params', None)
            headers = fetch_model.get('headers', None)

            request_kwargs = {
                'method': method,
                'url': endpoint
            }
            if headers:
                request_kwargs['headers'] = headers
            if params:
                request_kwargs['params'] = params
            if body:
                request_kwargs['data'] = body
            
            request = client.build_request(**request_kwargs)
            resp = await client.send(request)
            if resp.status_code != 200:
                raise Exception(f"Error fetching {endpoint} from {self.api_config.service_name}")
            else:
                return resp.json()

    @validate_credentials
    async def initiate_authorization(self, access_token):
        if not self.api_config.oauth_url_map:
            raise Exception(f"No oauth url map for {self.api_config.service_name}")
        
        authorization_config = self.api_config.oauth_url_map['initiate_authorization']
        endpoint = authorization_config.get('endpoint')
        method = authorization_config.get('method')
        params = authorization_config.get('params', None)
        headers = authorization_config.get('headers', None)
        body = None
        if method.lower() == "post":
            body = authorization_config.get('body', None)
        with httpx.AsyncClient(base_url=self.api_config.oauth_scheme['BASE_URL']) as client:
            request_kwargs = {
                'method': method.lower(),
                'url': endpoint,
            }
            if params:
                request_kwargs['params'] = params
            if headers:
                request_kwargs['headers'] = headers
            if body:
                request_kwargs['json'] = body
                
            request = client.build_request(**request_kwargs)
            response = await client.send(request)
            return response
        

            

        


