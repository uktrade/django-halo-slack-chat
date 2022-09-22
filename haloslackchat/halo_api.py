"""
Wrapper around Halo API using .

To simplify testing I keep these functions django free and pass in whats needed
in arguments. This can then be easily faked/mocked.


"""
import logging



def halo_ticket_url(halo_ticket_uri, ticket_id):
    """Return the link that can be stored in halo.

    This handles the trailing slach being present or not.

    """
    # handle trailing slash being there or not (urljoin doesn't).
    return '/'.join([halo_ticket_uri.rstrip('/'), str(ticket_id)])


def get_ticket(client, ticket_id):
    """Recover the ticket by it's ID in halo.

    :param client: The Halo web client to use.

    :param ticket_id: The Halo ID of the Ticket.

    :returns: A Halo.TicketAudit instance or None if nothing was found.

    """
    raise NotImplementedError


def create_ticket(
    client, chat_id, user_id, group_id, recipient_email, subject,
    slack_message_url
):
    """Create a new halo ticket in response to a new user question.

    :param client: The Halo web client to use.

    :param chat_id: The conversation ID on slack.

    :param user_id: Who to create the ticket as.

    :param group_id: Which group the ticket belongs to.

    :param recipient_email: The email addres to CC on the issue.

    :param subject: The title of the support issue.

    :param slack_message_url: The link to message on the support slack channel.

    :returns: A Ticket instance.

    """
    raise NotImplementedError


def add_comment(client, ticket, comment):
    """Add a new comment to an existing ticket.

    :param client: The Halo web client to use.

    :param ticket: The Halo Ticket instance to use.

    :param comment: The text for the Halo comment.

    :returns: The updated Ticket instance.

    """
    raise NotImplementedError


def close_ticket(client, ticket_id):
    """Close a ticket in halo.

    :param client: The Halo web client to use.

    :param ticket_id: The Halo Ticket ID.

    :returns: None or Ticket instance closed.

    """
    raise NotImplementedError
