from collections.abc import Awaitable
from typing import IO, Any, cast
import uuid

from aiobotocore.config import AioConfig
import aiobotocore.session

from src.infrastructure.storage.interface import SolutionStorage


class S3SolutionStorage(SolutionStorage):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        use_ssl: str,
    ) -> None:
        self._session = aiobotocore.session.get_session()
        self._config = AioConfig(signature_version="s3v4")
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket
        self._use_ssl = use_ssl

    async def upload_solution(self, file: IO[Any], filename: str, task_id: int, user_id: int) -> str:
        unique_id = uuid.uuid4().hex
        key = f"tasks/{task_id}/users/{user_id}/{unique_id}_{filename}"

        async with self._session.create_client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            config=self._config,
            use_ssl=self._use_ssl,
        ) as client:
            file_body = cast("bytes | Awaitable[bytes]", file.read())
            if isinstance(file_body, Awaitable):
                body_content = await file_body
            else:
                body_content = file_body
            await client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=body_content,
                ContentType="application/zip",
            )

        return key

    async def get_content(self, key: str) -> bytes:
        async with self._session.create_client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            config=self._config,
            use_ssl=self._use_ssl,
        ) as client:
            response = await client.get_object(Bucket=self._bucket, Key=key)
            async with response["Body"] as stream:
                data = await stream.read()
            return data
