from dotenv import load_dotenv
import os
import logging
import slack_bolt
from slack_sdk import WebClient
import datetime
import re


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
    title = event_title
    location = event_location
    event_title = re.sub(r"\s+", "+", event_title)
    event_location = re.sub(r"\s+", "+", event_location)
    link = f"https://time.cs50.io/{event_start}/{event_end}?title={event_title}&location={event_location}"
    return link, title, location, event_start, event_end


def extract_data_from_link(link):
    event_start = link.split("/")[3]
    event_end = link.split("/")[4].split("?")[0]
    event_title = link.split("?")[1].split("&")[0].split("=")[1]
    event_location = link.split("?")[1].split("&")[1].split("=")[1]
    event_desc = link.split("?")[1].split("&")[2].split("=")[1]
    event_title = re.sub(r"\+", " ", event_title)
    event_location = re.sub(r"\+", " ", event_location)
    return event_start, event_end, event_title, event_location


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
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Here's yr magical link: {link} for your {event_title} event at {event_location}.",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Google calendar"},
                        "url": f"https://www.google.com/calendar/render?action=TEMPLATE&text={event_title}&details=Event+Description&location=Event+Location&dates=YYYYMMDDTHHmmssZ/YYYYMMDDTHHmmssZ",
                        "style": "danger",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Apple calendar"},
                        "url": "https://apple.com",
                        "style": "danger",
                    },
                ],
            },
        ],
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


@app.event("link_shared")
def handle_link_shared(event, ack, client: WebClient):
    ack()
    print(event)
    links = event["links"]
    user = event["user"]
    for link in links:
        print(link)
        # extract_data_from_link(link)
        if user == "U078GJ63AQ0": # TODO: remove this check
            client.chat_postMessage(
                channel=event["channel"],
                thread_ts=event["message_ts"],
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"heyy, I see you shared a event url:{link['url']}! would you like to add this event to yr calenders??",
                        },
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Google calendar"},
                                "url": f"https://www.google.com/calendar/render?action=TEMPLATE&text=event_title&details=Event+Description&location=event_location&dates=YYYYMMDDTHHmmssZ/YYYYMMDDTHHmmssZ",
                                "style": "danger",
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Apple calendar"},
                                "url": "https://apple.com",
                                "style": "danger",
                            },
                        ],
                    },
                ],
            )
        else:
            print("unauthorized user")