import uuid

import lib.clients as _clients
import lib.sanatorium.models as _sanatorium_models


class UserService:
    def __init__(
        self,
        http_client: _clients.AsyncHttpClient,
    ):
        self.http_client = http_client

    async def create(self, request: _sanatorium_models.UserInfoModel) -> _sanatorium_models.UserFullModel:
        response = await self.http_client.post("/users/", json=request.model_dump(mode="json"))
        response_model = _sanatorium_models.UserFullModel(**response.json())
        return response_model
