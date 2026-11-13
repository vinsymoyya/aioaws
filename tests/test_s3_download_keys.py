import pytest
from httpx2 import URL, AsyncClient

from aioaws.s3 import S3Client, S3Config


@pytest.mark.parametrize(
    'key', ['reports/a?b.txt', 'reports/a#b.txt', 'reports/a%2Fb.txt', 'reports/caf\u00e9 file.txt']
)
async def test_signed_download_preserves_the_object_key(key):
    async with AsyncClient() as client:
        s3 = S3Client(client, S3Config('testing', 'testing', 'us-east-1', 'test-bucket'))
        url = URL(s3.signed_download_url(key))
    assert url.path == '/' + key
    assert url.fragment == ''
