import pytest
from httpx2 import Request

from aioaws.core import AWSv4Auth


@pytest.mark.parametrize('url', ['https://localhost:9443/test', 'https://[::1]:9443/test', 'https://example.com/test'])
def test_signed_host_matches_request_authority(url):
    request = Request('GET', url)
    auth = AWSv4Auth('secret', 'access', 'us-east-1', 's3')
    assert auth.auth_headers('GET', request.url)['host'] == request.headers['host']
