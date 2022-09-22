import os

from celery import Celery
from celery.schedules import crontab

from haloslackchat import botlogging

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')

botlogging.log_setup()

app = Celery('django-halo-slack-chat')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = 'Europe/London'
# Allow me to configure my own logging and not use celery's way of doing it.
app.conf.worker_hijack_root_logger = False


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up the daily report.
    """
    sender.add_periodic_task(
        # 9:00am Monday to Friday
        crontab(hour=9, minute=0, day_of_week='1-5'),
        run_daily_summary,
    )


@app.task(ignore_result=True)
def run_daily_summary():
    """Generate and send the daily summary report to slack.
    """
    from webapp import settings
    from haloslackchat.models import SlackApp
    from haloslackchat.models import HaloSlackChat

    channel_id = settings.SRE_SUPPORT_CHANNEL
    workspace_uri = settings.SLACK_WORKSPACE_URI

    report_data = HaloSlackChat.daily_summary(workspace_uri)
    text = HaloSlackChat.daily_report(report_data)

    client = SlackApp.client()
    client.chat_postMessage(channel=channel_id, text=text)
