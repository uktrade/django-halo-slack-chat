import json
import datetime
from unittest.mock import patch
from unittest.mock import MagicMock

import pytest
from django.test import RequestFactory, TestCase
from rest_framework.test import APIRequestFactory

from haloslackchat.models import SlackApp
from haloslackchat.models import HaloApp
from haloslackchat import halo_webhooks
from haloslackchat import halo_base_webhook


def test_halo_request_is_rejected_with_missing_token_field():
    """Test if no token is present when data is POSTed to the 
    halo webhook webhook.

    """
    halo_event = {
        # no token in request
        # 'token': '...',
        'external_id': '1603983778.011500',
        'ticket_id': '1430',
    }
    factory = APIRequestFactory()
    view = halo_base_webhook.BaseWebHook.as_view()
    request = factory.post(
        '/halo/webhook/', 
        halo_event,
        format='json'
    )
    response = view(request)
    assert response.status_code == 403


def test_halo_request_token_is_incorrect():
    """Test that presenting the wrong token rejects the request.
    """
    halo_event = {
        'token': 'not-the-right-token',
        'external_id': '1603983778.011500',
        'ticket_id': '1430',
    }
    factory = APIRequestFactory()
    view = halo_base_webhook.BaseWebHook.as_view()
    request = factory.post(
        '/halo/webhook/', 
        halo_event,
        format='json'
    )
    override = {'HALO_WEBHOOK_TOKEN': 'the-correct-token'}
    with patch.dict('webapp.settings.__dict__', override):    
        response = view(request)

    assert response.status_code == 403


@patch('haloslackchat.halo_base_webhook.SlackApp')
@patch('haloslackchat.halo_base_webhook.HaloApp')
@patch('haloslackchat.halo_webhooks.comments_from_halo')
def test_halo_exception_raised_by_update_comments(
    comments_from_halo, HaloApp, SlackApp, log, db
):
    """Test that 200 ok is returned even if update blows up internally.
    """
    halo_event = {
        'token': 'the-correct-token',
        'external_id': '1603983778.011500',
        'ticket_id': '1430',
    }
    factory = APIRequestFactory()
    view = halo_webhooks.CommentsWebHook.as_view()
    request = factory.post(
        '/halo/webhook/', 
        halo_event,
        format='json'
    )

    comments_from_halo.side_effect = ValueError(
        'fake problem occurred internally'
    )

    override = {'HALO_WEBHOOK_TOKEN': 'the-correct-token'}
    with patch.dict('webapp.settings.__dict__', override):    
        response = view(request)

    assert response.status_code == 200
    comments_from_halo.assert_called()


@pytest.mark.parametrize(
    (
        'WebHookView', 'patch_path', 'halo_event', 'env'
    ),
    (
        (
            halo_webhooks.EmailWebHook, 
            'haloslackchat.halo_webhooks.email_from_halo',
            {
                'token': 'the-correct-token',
                'ticket_id': '32',
                'channel_id': 'slack-channel-id',
                'halo_uri': 'https://z.e.n.d.e.s.k',
                'workspace_uri': 'https://s.l.a.c.k'
            },
            {
                'HALO_WEBHOOK_TOKEN': 'the-correct-token',
                'SRE_SUPPORT_CHANNEL': 'slack-channel-id',
                'HALO_REDIRECT_URI': 'https://z.e.n.d.e.s.k',
                'SLACK_WORKSPACE_URI': 'https://s.l.a.c.k'
            }
        ),
        (
            halo_webhooks.CommentsWebHook, 
            'haloslackchat.halo_webhooks.comments_from_halo',
            {
                'token': 'the-correct-token',
                'ticket_id': '1430',
            },
            {
                'HALO_WEBHOOK_TOKEN': 'the-correct-token'
            }            
        ),
    )
)
@patch('haloslackchat.halo_base_webhook.SlackApp')
@patch('haloslackchat.halo_base_webhook.HaloApp')
@patch('haloslackchat.halo_webhooks.email_from_halo')
def test_halo_webhook_events_ok_path(
    email_from_halo, HaloApp, SlackApp,
    WebHookView, patch_path, halo_event, env,
    log, db
):
    """Test OK cases for Halo webhooks.
    """
    class MockClient:
        def __init__(self, name):
            self.name = name

    SlackApp.client = MagicMock()
    slack_client = MockClient('slack')
    SlackApp.client.return_value = slack_client
    # test my understanding of who this should work
    assert SlackApp.client() == slack_client

    HaloApp.client = MagicMock()
    halo_client = MockClient('halo')
    HaloApp.client.return_value = halo_client
    assert HaloApp.client() == halo_client
    with patch(patch_path) as expected_function_call:    
        with patch.dict('webapp.settings.__dict__', env):    
            view = WebHookView.as_view()
            factory = APIRequestFactory()
            request = factory.post(
                '/halowebhook/', 
                halo_event,
                format='json'
            )
            response = view(request)

    assert response.status_code == 200
    SlackApp.client.assert_called()
    HaloApp.client.assert_called()
    expected_function_call.assert_called_with(
        halo_event,
        slack_client,
        halo_client
    )