import pytest
from httpx2 import AsyncClient, MockTransport, Response

from aioaws.core import RequestError
from aioaws.s3 import S3Client, S3Config


async def test_delete_does_not_report_failed_objects_as_deleted():
    body = b"""<DeleteResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
      <Deleted><Key>allowed.txt</Key></Deleted>
      <Error><Key>denied.txt</Key><Code>AccessDenied</Code><Message>Access denied</Message></Error>
    </DeleteResult>"""
    async with AsyncClient(transport=MockTransport(lambda request: Response(200, content=body))) as client:
        s3 = S3Client(client, S3Config('testing', 'testing', 'us-east-1', 'test-bucket'))
        with pytest.raises(RequestError) as caught:
            await s3.delete('allowed.txt', 'denied.txt')
        assert caught.value.response.content == body
