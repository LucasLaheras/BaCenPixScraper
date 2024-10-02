import os
import requests
import json
from typing import Optional


class TeamsNotifier:
    """A class to send messages to a Microsoft Teams channel using Incoming Webhooks."""

    def __init__(self, webhook_url: str):
        """
        Initialize the TeamsNotifier with the webhook URL.

        Args:
            webhook_url (str): The Microsoft Teams Incoming Webhook URL.
        """
        self.webhook_url = webhook_url

    def send_message(self, title: str, message: str):
        """
        Send a message to the Microsoft Teams channel.

        Args:
            title (str): The title of the message.
            message (str): The body of the message.
        """
        payload = {
            "title": title,
            "text": message
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.webhook_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            print("Message sent to Microsoft Teams successfully.")
        except requests.exceptions.HTTPError as err:
            print(f"Error sending message to Microsoft Teams: {err}")
        except requests.exceptions.RequestException as err:
            print(f"Request exception: {err}")


# Usage example:
if __name__ == "__main__":
    # Microsoft Teams webhook setup
    TEAMS_WEBHOOK_URL = 'Input here https://teams_link'
    teams_notifier = TeamsNotifier(webhook_url=TEAMS_WEBHOOK_URL)

    if not TEAMS_WEBHOOK_URL:
        print("Error: TEAMS_WEBHOOK_URL environment variable not set.")
        exit(1)

    # Send a test message
    teams_notifier.send_message(
        title="Test Notification",
        message="This is a test message sent to Microsoft Teams via Incoming Webhook."
    )