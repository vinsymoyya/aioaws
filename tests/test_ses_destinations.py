from email.message import EmailMessage
from urllib.parse import parse_qs

from httpx2 import AsyncClient, MockTransport, Request, Response

from aioaws.ses import SesClient, SesConfig, SesRecipient


async def test_raw_email_envelope_destinations():
    sent_form: dict[str, list[str]] = {}

    def handle_request(request: Request) -> Response:
        sent_form.update(parse_qs(request.content.decode()))
        return Response(200, content=b'<MessageId>test-message-id</MessageId>')

    message = EmailMessage()
    message['Subject'] = 'Envelope destinations'
    message['From'] = 'sender@example.com'
    message['To'] = 'visible-recipient@example.com'
    message.set_content('Message body')

    async with AsyncClient(transport=MockTransport(handle_request)) as client:
        ses = SesClient(client, SesConfig('test_access_key', 'test_secret_key', 'testing-region-1'))
        message_id = await ses.send_raw_email(
            'sender@example.com',
            message,
            to=[SesRecipient('to1@example.com'), SesRecipient('to2@example.com', 'To', 'Recipient')],
            cc=[SesRecipient('cc@example.com')],
            bcc=[SesRecipient('bcc@example.com')],
        )

    assert message_id == 'test-message-id'
    assert {key: value for key, value in sent_form.items() if key not in {'Action', 'Source', 'RawMessage.Data'}} == {
        'Destinations.member.1': ['to1@example.com'],
        'Destinations.member.2': ['to2@example.com'],
        'Destinations.member.3': ['cc@example.com'],
        'Destinations.member.4': ['bcc@example.com'],
    }
    assert message['To'] == 'visible-recipient@example.com'
