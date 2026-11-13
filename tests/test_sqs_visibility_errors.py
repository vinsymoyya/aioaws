import pytest
from httpx2 import AsyncClient, HTTPStatusError, MockTransport, Request, Response

from aioaws.sqs import AWSAuthConfig, SQSClient, SQSMessage


@pytest.mark.asyncio
@pytest.mark.parametrize('status_code', [400, 403, 429, 500])
async def test_change_visibility_propagates_http_errors(status_code: int) -> None:
    def handler(request: Request) -> Response:
        assert request.url.params['Action'] == 'ChangeMessageVisibility'
        return Response(status_code, json={'Error': {'Code': 'RequestFailed'}})

    async with AsyncClient(transport=MockTransport(handler)) as client:
        sqs = SQSClient(
            'https://sqs.us-east-1.amazonaws.com/123456789012/test',
            AWSAuthConfig(aws_access_key='test', aws_secret_key='test', aws_region='us-east-1'),
            client=client,
        )
        message = SQSMessage(message_id='id', receipt_handle='receipt', md5_of_body='md5', body='body', attributes={})

        with pytest.raises(HTTPStatusError) as exc_info:
            await sqs.change_visibility(message, 30)

        assert exc_info.value.response.status_code == status_code
