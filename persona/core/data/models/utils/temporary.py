from typing import Optional, Any

from pydantic import BaseModel

class TemporaryModel(BaseModel):
    uuid: str;
    tag: str;
    data: Optional[Any];

    def get_data(self):
        return dict(self.data)
