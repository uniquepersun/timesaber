from dotenv import load_dotenv
import os
import logging
import slack_bolt
from slack_sdk import WebClient


logging.basicConfig(level=logging.DEBUG)
load_dotenv()

app = slack_bolt.App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

@app.command("/create_eventtime_link")
@app.shortcut("tttnnn")
def handle_app_mention(body, logger, ack, client:WebClient):
    ack()
    logger.info(body)

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
	"title": {
		"type": "plain_text",
		"text": "timesaber!",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Get magical link",
		"emoji": True
	},
	"type": "modal",
	"close": {
		"type": "plain_text",
		"text": "No thanks",
		"emoji": True
	},
	"blocks": [
		{
			"type": "input",
			"block_id": "event_title",
			"element": {
				"type": "plain_text_input",
				"action_id": "event_title_info",
				"placeholder": {
					"type": "plain_text",
					"text": "title goes here.."
				}
			},
			"label": {
				"type": "plain_text",
				"text": "What is it??",
				"emoji": True
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://pbs.twimg.com/profile_images/625633822235693056/lNGUneLX_400x400.jpg",
					"alt_text": "cute cat"
				},
				{
					"type": "mrkdwn",
					"text": "*Cat* has approved this message."
				}
			]
		},
		{
			"type": "input",
			"block_id": "event_location",
			"element": {
				"type": "plain_text_input",
				"action_id": "event_location_info",
				"placeholder": {
					"type": "plain_text",
					"text": "you can put channel/msg links too yay"
				}
			},
			"label": {
				"type": "plain_text",
				"text": "Where will it happen?",
				"emoji": True
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://pbs.twimg.com/profile_images/625633822235693056/lNGUneLX_400x400.jpg",
					"alt_text": "cute cat"
				},
				{
					"type": "mrkdwn",
					"text": "*Cat* has approved this message."
				}
			]
		},
		{
			"type": "input",
			"block_id": "event_start",
			"element": {
				"type": "datetimepicker",
				"action_id": "event_start_time"
			},
			"label": {
				"type": "plain_text",
				"text": "When yr event starting??",
				"emoji": True
			}
		},
		{
			"type": "input",
			"block_id": "event_end",
			"element": {
				"type": "datetimepicker",
				"action_id": "event_end_time"
			},
			"label": {
				"type": "plain_text",
				"text": "When is it gonna end?",
				"emoji": True
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://pbs.twimg.com/profile_images/625633822235693056/lNGUneLX_400x400.jpg",
					"alt_text": "cute cat"
				},
				{
					"type": "mrkdwn",
					"text": "*Cat* has approved this message."
				}
			]
		}
	]
}
    )