from httpx2 import URL

from aioaws.s3 import S3Client, S3Config


def test_cache_version_is_included_in_signature(mocker):
    s3 = S3Client(None, S3Config('testing', 'testing', 'us-east-1', 'test-bucket'))
    sign = mocker.spy(s3._aws_client._auth, 'aws4_signature')
    url = URL(s3.signed_download_url('test.txt', version='revision 2'))
    assert sign.call_args.args[2].params['v'] == 'revision 2'
    assert url.params['v'] == 'revision 2'
