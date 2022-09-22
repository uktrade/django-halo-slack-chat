"""
Functions that handle messages from Halo via triggers.
"""
import logging

from webapp import settings
from haloslackchat.models import SlackApp
from haloslackchat.models import HaloApp
from haloslackchat.models import PagerDutyApp
from haloslackchat.models import HaloSlackChat
from haloslackchat.slack_api import message_url
from haloslackchat.slack_api import create_thread
from haloslackchat.halo_api import get_ticket
from haloslackchat.halo_api import add_comment
from haloslackchat.message_tools import message_issue_halo_url
from haloslackchat.message_tools import message_who_is_on_call


def email_from_halo(event, slack_client, halo_client):
    """Open a HaloSlackChat issue and link it to the existing Ticket.

    """
    log = logging.getLogger(__name__)

    halo = HaloApp.client()
    slack = SlackApp.client()
    ticket_id = event['ticket_id']
    channel_id = settings.SRE_SUPPORT_CHANNEL
    user_id = settings.HALO_USER_ID
    group_id = settings.HALO_GROUP_ID
    halo_ticket_uri = settings.HALO_TICKET_URI
    slack_workspace_uri = settings.SLACK_WORKSPACE_URI

    # Recover the halo issue the email has already created:
    log.debug(f'Recovering ticket from Halo:<{ticket_id}>')
    ticket = get_ticket(halo, ticket_id)

    # We need to create a new thread for this on the slack channel.
    # We will then add the usual message to this new thread.
    log.debug(f'Success. Got Halo ticket<{ticket_id}>')
    # Include descrition as next comment before who is on call to slack
    # to give SREs more context:
    message = f"(From Halo Email): {ticket.subject}"
    chat_id = create_thread(slack, channel_id, message)

    # Assign the ticket to HaloSlackChat group and user so comments will
    # come back to us on slack.
    log.debug(
        f'Assigning Halo ticket to User:<{user_id}> and Group:{group_id}'
    )
    # Assign to User/Group
    ticket.assingee_id = user_id
    ticket.group_id = group_id
    # Set to route comments back from halo to slack:
    ticket.external_id = chat_id
    halo.tickets.update(ticket) ##TODO zenpy specific

    # Store the halo ticket in our db and notify:
    HaloSlackChat.open(channel_id, chat_id, ticket_id=ticket.id)
    message_issue_halo_url(
        slack_client, halo_ticket_uri, ticket_id, chat_id, channel_id
    )
    message_who_is_on_call(
        PagerDutyApp.on_call(), slack_client, chat_id, channel_id
    )

    # Indicate on the existing Halo ticket that the SRE team now knows
    # about this issue.
    slack_chat_url = message_url(slack_workspace_uri, channel_id, chat_id)
    add_comment(
        halo_client,
        ticket,
        f'The SRE team is aware of your issue on Slack here {slack_chat_url}.'
    )
