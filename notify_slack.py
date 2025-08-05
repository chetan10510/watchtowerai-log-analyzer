import requests
import os
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(log_message, s3_link=None):
    if not SLACK_WEBHOOK_URL:
        print(" Slack webhook URL not found in .env")
        return

    text = f"* Incident Detected!*\n```{log_message}```"
    if s3_link:
        text += f"\n [Runbook]({s3_link})"

    payload = {
        "text": text,
        "mrkdwn": True
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        print(" Slack alert sent.")
    else:
        print(f" Slack alert failed: {response.status_code} - {response.text}")
