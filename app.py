import os
import sys
import json

import requests
from flask import Flask, request
from wit import Wit


app = Flask(__name__)

WIT_TOKEN = os.environ["WIT_TOKEN"]
FB_PAGE_TOKEN = os.environ["FB_PAGE_TOKEN"]
FB_VERIFY_TOKEN = os.environ["FB_VERIFY_TOKEN"]

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == FB_VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Sup", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    #message was sent
                    sender_id = messaging_event["sender"]["id"]
                    # recipient id is your fb id
                    message_text = messaging_event["message"]["text"]

#setup actions
actions = {
    'send': send,
    'addReminder': add_reminder,
}

# setup wit client
client = Wit(access_token=WIT_TOKEN, actions=actions)

