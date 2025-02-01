from dotenv import load_dotenv
import os
import logging
import slack_bolt
from slack_sdk import WebClient
import datetime


logging.basicConfig(level=logging.DEBUG)
load_dotenv()

app = slack_bolt.App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


def epochtoiso(returnedtimestamp):
    return datetime.datetime.fromtimestamp(returnedtimestamp).isoformat()


def extractdata(body, logger):
    event_title = body["view"]["state"]["values"]["event_title"]["event_title_info"][
        "value"
    ]
    logger.info(event_title)
    event_location = body["view"]["state"]["values"]["event_location"][
        "event_location_info"
    ]["value"]
    logger.info(event_location)
    event_start = epochtoiso(
        int(
            body["view"]["state"]["values"]["event_start"]["event_start_time"][
                "selected_date_time"
            ]
        )
    )
    logger.info(event_start)
    event_end = epochtoiso(
        int(
            body["view"]["state"]["values"]["event_end"]["event_end_time"][
                "selected_date_time"
            ]
        )
    )
    logger.info(event_end)
    return event_title, event_location, event_start, event_end


def create_link(body, logger):
    event_title, event_location, event_start, event_end = extractdata(body, logger)
    link = f"https://time.cs50.io/{event_start}/{event_end}?title={event_title}&location={event_location}"
    return link, event_title, event_location, event_start, event_end


@app.command("/createeventtimelink")
@app.shortcut("tttnnn")
def handle_shortcut_usage(body, logger, ack, client: WebClient):
    ack()
    logger.info(body)

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "title": {"type": "plain_text", "text": "timesaber!", "emoji": True},
            "submit": {"type": "plain_text", "text": "Get magical link", "emoji": True},
            "type": "modal",
            "callback_id": "tttnnn",
            "close": {"type": "plain_text", "text": "No thanks", "emoji": True},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "event_title",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "event_title_info",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "title goes here..",
                        },
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "What is it??",
                        "emoji": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "event_location",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "event_location_info",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "you can put channel/msg links too yay",
                        },
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Where will it happen?",
                        "emoji": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "event_start",
                    "element": {
                        "type": "datetimepicker",
                        "action_id": "event_start_time",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "When yr event starting??",
                        "emoji": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "event_end",
                    "element": {
                        "type": "datetimepicker",
                        "action_id": "event_end_time",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "When is it gonna end?",
                        "emoji": True,
                    },
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "image",
                            "image_url": "https://pbs.twimg.com/profile_images/625633822235693056/lNGUneLX_400x400.jpg",
                            "alt_text": "cute cat",
                        },
                        {"type": "mrkdwn", "text": "*Cat* has approved this message."},
                    ],
                },
            ],
        },
    )


@app.view("tttnnn")
def handle_view_submission(ack, body, logger, client: WebClient):
    ack()
    logger.info(f"Data recieved; Recieved data:{body}")
    event_data = create_link(body, logger)
    link = event_data[0]
    event_title = event_data[1]
    event_location = event_data[2]
    user = body["user"]["id"]
    client.chat_postMessage(
        channel=user,
        text=f"Here's yr magical link: {link} for your {event_title} event at {event_location}.",
    )
    # TODO: show a modal with the link instead of sending msg(erroring for now) & also log them on the home tab with all event info
    # client.views_push(
    #     trigger_id=body["trigger_id"],
    #     view={
    #         "title": {"type": "plain_text", "text": "Here's yr magical link!"},
    #         "type": "modal",
    #         "callback_id": "modal_copy_link",
    #         "close": {"type": "plain_text", "text": "thank you", "emoji": True},
    #         "blocks": [
    #             {
    #                 "type": "section",
    #                 "text": {
    #                     "type": "mrkdwn",
    #                     "text": f"yr link: {link}.",
    #                 },
    #             }
    #         ],
    #     },
    # )
    