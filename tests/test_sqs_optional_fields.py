from typing import Any

import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from aioaws.sqs import AWSAuthConfig, SQSClient, SQSMessage


@pytest.mark.asyncio
@pytest.mark.parametrize('receive_result', [{}, {'messages': []}, {'messages': None}])
async def test_poll_handles_empty_message_lists(receive_result: dict[str, Any]) -> None:
    def handler(request: Request) -> Response:
        return Response(200, json={'ReceiveMessageResponse': {'ReceiveMessageResult': receive_result}})

    async with AsyncClient(transport=MockTransport(handler)) as client:
        sqs = SQSClient(
            'https://sqs.us-east-1.amazonaws.com/123456789012/test',
            AWSAuthConfig(aws_access_key='test', aws_secret_key='test', aws_region='us-east-1'),
            client=client,
        )
        poll = sqs.poll()
        try:
            assert await anext(poll) == []
        finally:
            await poll.aclose()


@pytest.mark.asyncio
async def test_poll_handles_messages_without_requested_attributes() -> None:
    def handler(request: Request) -> Response:
        return Response(
            200,
            json={
                'ReceiveMessageResponse': {
                    'ReceiveMessageResult': {
                        'messages': [
                            {'MessageId': 'id', 'ReceiptHandle': 'receipt', 'MD5OfBody': 'md5', 'Body': 'body'}
                        ]
                    }
                }
            },
        )

    async with AsyncClient(transport=MockTransport(handler)) as client:
        sqs = SQSClient(
            'https://sqs.us-east-1.amazonaws.com/123456789012/test',
            AWSAuthConfig(aws_access_key='test', aws_secret_key='test', aws_region='us-east-1'),
            client=client,
        )
        poll = sqs.poll()
        try:
            assert await anext(poll) == [
                SQSMessage(message_id='id', receipt_handle='receipt', md5_of_body='md5', body='body', attributes={})
            ]
        finally:
            await poll.aclose()
