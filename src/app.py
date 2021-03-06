"""app.py - Forwards webhook events as messages to bot.py."""

from flask import Flask
from bot import WebhookBot
from flask_hookserver import Hooks
from webhooks import GithubWebhookConsumer
from settings import settings

app = Flask(__name__)

app.config['GITHUB_WEBHOOKS_KEY'] = settings.get('github_webhook_secret')
app.config['VALIDATE_IP'] = settings.get('github_validate_ip', False)
app.config['VALIDATE_SIGNATURE'] = settings.get('github_validate_signature', True)  # NOQA

bot = WebhookBot(settings)
webhook_consumer = GithubWebhookConsumer(bot)
hooks = Hooks(app, bot.hooks_endpoint)


@hooks.hook('ping')
def ping_webhook(payload, guid):
    """Handle GitHub Ping (sent when webhook is created)."""
    return webhook_consumer.process(payload, 'ping')


@hooks.hook('issues')
def issue_webhook(payload, guid):
    """Handle GitHub Issue Events."""
    return webhook_consumer.process(payload, 'issues')


@hooks.hook('pull_request')
def pull_request_webhook(payload, guid):
    """Handle GitHub Pull Request Events."""
    return webhook_consumer.process(payload, 'pull_request')


if __name__ == '__main__':
    try:
        bot.run(block=False)
        app.run(debug=True, host='0.0.0.0', port=8080)
    except (KeyboardInterrupt, SystemExit):
        bot.cleanup()
