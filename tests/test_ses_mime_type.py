import pytest
from foxglove.testing import DummyServer
from httpx2 import AsyncClient

from aioaws.ses import SesAttachment, SesClient, SesConfig


@pytest.mark.parametrize(
    'name,mime_type',
    [('invoice.bin', 'application/pdf'), ('archive.tar.gz', 'application/gzip'), (None, 'image/png')],
)
async def test_explicit_attachment_mime_type(client: AsyncClient, aws: DummyServer, name, mime_type):
    ses = SesClient(client, SesConfig('test_access_key', 'test_secret_key', 'testing-region-1'))

    await ses.send_email(
        'sender@example.com',
        'Explicit attachment type',
        ['recipient@example.com'],
        'Message body',
        attachments=[SesAttachment(file=b'attachment content', name=name, mime_type=mime_type)],
    )

    attachment = aws.app['emails'][0]['email']['payload'][1]
    assert attachment['Content-Type'] == mime_type
    assert attachment['payload'] == 'attachment content'
