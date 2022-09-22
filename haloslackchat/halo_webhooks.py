from haloslackchat.halo_base_webhook import BaseWebHook
from haloslackchat.halo_email_to_slack import email_from_halo
from haloslackchat.halo_comments_to_slack import comments_from_halo


class CommentsWebHook(BaseWebHook):
    """Handle Halo Comment Events.
    """
    def handle_event(self, event, slack_client, halo_client):
        """Handle the comment trigger event we have been POSTed.

        Recover and update the comments with lastest from Halo.

        """
        comments_from_halo(event, slack_client, halo_client)


class EmailWebHook(BaseWebHook):
    """Handle Halo Email Events.
    """
    def handle_event(self, event, slack_client, halo_client):
        """Handle an email created issue and create it on slack.
        """
        email_from_halo(event, slack_client, halo_client)
