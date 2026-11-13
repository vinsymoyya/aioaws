from datetime import UTC, datetime

import pytest
from httpx2 import AsyncClient

from aioaws.ses import SesWebhookInfo


@pytest.mark.parametrize('type_field', ['eventType', 'notificationType'])
@pytest.mark.parametrize(
    'notification_type,details,unsubscribe',
    [('Bounce', {'bounceType': 'Permanent'}, True), ('Complaint', {}, True), ('Delivery', {}, False)],
)
async def test_ses_notification_type(
    client: AsyncClient, build_sns_webhook, type_field, notification_type, details, unsubscribe
):
    message = {
        type_field: notification_type,
        'mail': {'messageId': 'message-id', 'timestamp': '2026-11-13T12:00:00Z'},
        notification_type.lower(): details,
    }

    info = await SesWebhookInfo.build(build_sns_webhook(message), client)

    assert info is not None
    assert info.event_type == notification_type.lower()
    assert info.message_id == 'message-id'
    assert info.timestamp == datetime(2026, 11, 13, 12, tzinfo=UTC)
    assert info.unsubscribe is unsubscribe
    assert info.details == details
    assert info.full_message == message
