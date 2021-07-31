from pydantic import BaseModel, Field

from typing import Any


class SpotifyStatistic(BaseModel):
    # User data
    user_id: str = Field(...)
    spotify_id: str = Field(...)
    tag: str = Field(...)
    label: str = Field(...)
    data: Any = Field(...)

    display_method: str = Field(...)
