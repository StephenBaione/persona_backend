from typing import Any, Optional
from pydantic import BaseModel, Field, create_model

from core.data.models.auth.token import Token

class APIConfig(BaseModel):
    oauth_scheme: Optional[str] = None
    """
    URL MAP Schema:
    BASE_URL: str
    'initiate_authorization': 
        'endpoint': str
        'params': dict,
        'headers': str,
        'body': str,
        'method': str,
    'redirect': str,
    'request_token': str,
    'refresh_token': str
    """
    oauth_url_map: Optional[dict] = None
    token: Optional[Token] = None
    

    service_name: str = Field(...)

    """
    URL MAP Schema:
    section: {
        BASE_URL: str,
        model_key:
            'endpoint': str
            'method'
            'params': dict,
            'headers': str,
            'body': str,
            'method': str
    }
    """
    url_map: dict = Field(...)

