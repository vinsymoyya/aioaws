import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from aioaws.sqs import AWSAuthConfig, SQSClient, SQSMessage


@pytest.mark.asyncio
@pytest.mark.parametrize('timeout', [0, 43200])
async def test_change_visibility_accepts_inclusive_limits(timeout: int) -> None:
    sent_timeouts: list[str] = []

    def handler(request: Request) -> Response:
        sent_timeouts.append(request.url.params['VisibilityTimeout'])
        return Response(200)

    async with AsyncClient(transport=MockTransport(handler)) as client:
        sqs = SQSClient(
            'https://sqs.us-east-1.amazonaws.com/123456789012/test',
            AWSAuthConfig(aws_access_key='test', aws_secret_key='test', aws_region='us-east-1'),
            client=client,
        )
        message = SQSMessage(message_id='id', receipt_handle='receipt', md5_of_body='md5', body='body', attributes={})

        await sqs.change_visibility(message, timeout)

    assert sent_timeouts == [str(timeout)]


@pytest.mark.asyncio
@pytest.mark.parametrize('timeout', [-1, 43201])
async def test_change_visibility_rejects_out_of_range_values(timeout: int) -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(200)

    async with AsyncClient(transport=MockTransport(handler)) as client:
        sqs = SQSClient(
            'https://sqs.us-east-1.amazonaws.com/123456789012/test',
            AWSAuthConfig(aws_access_key='test', aws_secret_key='test', aws_region='us-east-1'),
            client=client,
        )
        message = SQSMessage(message_id='id', receipt_handle='receipt', md5_of_body='md5', body='body', attributes={})

        with pytest.raises(ValueError, match=f'^timeout value range is 0 to 43200, got {timeout}$'):
            await sqs.change_visibility(message, timeout)

    assert requests == []
