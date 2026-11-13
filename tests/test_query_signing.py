import hashlib
from datetime import datetime

import pytest
from httpx2 import URL

from aioaws.core import AWSv4Auth


@pytest.mark.parametrize('query', ['z=last&prefix=a+b', 'prefix=a%20b&z=last', 'z=last&prefix=a%20b'])
def test_query_signing_uses_sorted_uri_encoded_parameters(query, mocker):
    auth = AWSv4Auth('secret', 'access', 'us-east-1', 's3')
    sign = mocker.patch.object(auth, 'aws4_sign_string', return_value='signature')
    auth.aws4_signature(
        datetime(2013, 5, 24),
        'GET',
        URL('https://example.com/test.txt?' + query),
        {'host': 'example.com'},
        'UNSIGNED-PAYLOAD',
    )
    canonical = 'GET\n/test.txt\nprefix=a%20b&z=last\nhost:example.com\n\nhost\nUNSIGNED-PAYLOAD'
    assert sign.call_args.args[0].splitlines()[-1] == hashlib.sha256(canonical.encode()).hexdigest()


def test_query_signing_sorts_encoded_names_and_duplicate_values(mocker):
    auth = AWSv4Auth('secret', 'access', 'us-east-1', 's3')
    sign = mocker.patch.object(auth, 'aws4_sign_string', return_value='signature')
    auth.aws4_signature(
        datetime(2013, 5, 24),
        'GET',
        URL('https://example.com/?z=last&a=2&a=1&%C3%A9=x'),
        {'host': 'example.com'},
        'UNSIGNED-PAYLOAD',
    )
    canonical = 'GET\n/\n%C3%A9=x&a=1&a=2&z=last\nhost:example.com\n\nhost\nUNSIGNED-PAYLOAD'
    assert sign.call_args.args[0].splitlines()[-1] == hashlib.sha256(canonical.encode()).hexdigest()


def test_sqs_receipt_handle_slashes_are_encoded_for_signing(mocker):
    auth = AWSv4Auth('secret', 'access', 'us-east-1', 'sqs')
    sign = mocker.patch.object(auth, 'aws4_sign_string', return_value='signature')
    auth.aws4_signature(
        datetime(2013, 5, 24),
        'POST',
        URL('https://example.com/?Action=DeleteMessage&ReceiptHandle=abc/def%2Bghi%3D'),
        {'host': 'example.com'},
        'UNSIGNED-PAYLOAD',
    )
    canonical = (
        'POST\n/\nAction=DeleteMessage&ReceiptHandle=abc%2Fdef%2Bghi%3D\nhost:example.com\n\nhost\nUNSIGNED-PAYLOAD'
    )
    assert sign.call_args.args[0].splitlines()[-1] == hashlib.sha256(canonical.encode()).hexdigest()
