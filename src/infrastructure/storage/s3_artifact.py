from aiobotocore.config import AioConfig
import aiobotocore.session

from src.infrastructure.storage.artifact import SolutionArtifactStorage


class S3SolutionArtifactStorage(SolutionArtifactStorage):
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

    @staticmethod
    def _make_key(solution_id: int, key: str) -> str:
        return f"{solution_id}/{key}.md"

    async def save_artifact(self, solution_id: int, key: str, content: str) -> None:
        full_key = self._make_key(solution_id, key)
        async with self._session.create_client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            config=self._config,
            use_ssl=self._use_ssl,
        ) as client:
            await client.put_object(
                Bucket=self._bucket,
                Key=full_key,
                Body=content.encode("utf-8"),
                ContentType="text/plain; charset=utf-8",
            )

    async def get_artifact(self, solution_id: int, key: str) -> str:
        full_key = self._make_key(solution_id, key)
        async with self._session.create_client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            config=self._config,
            use_ssl=self._use_ssl,
        ) as client:
            response = await client.get_object(Bucket=self._bucket, Key=full_key)
            async with response["Body"] as stream:
                data = await stream.read()
                return data.decode("utf-8")

    async def delete_artifact(self, solution_id: int, key: str) -> None:
        full_key = self._make_key(solution_id, key)
        async with self._session.create_client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            config=self._config,
            use_ssl=self._use_ssl,
        ) as client:
            await client.delete_object(Bucket=self._bucket, Key=full_key)
