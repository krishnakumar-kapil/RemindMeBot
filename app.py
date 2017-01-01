import os
import sys
import json
#import tz
from redis import Redis
#from rq_scheduler import Scheduler
from datetime import datetime
from rq import Queue

import requests
from flask import Flask, request
from wit import Wit

"""
TODO:
timezone first
based on that do the messages
implement the messaging queues using celery
use rq instead



"""
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
    #log(data)

    """
    handler for event handling
    """
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    #message was sent
                    sender_id = messaging_event["sender"]["id"]
                    # recipient id is your fb id
                    message_text = messaging_event["message"]["text"]
                    fb_message(sender_id, "received message")
                    log("message_text_received: "+message_text);
                    #get the wit to do stuff
                    if("remind" in message_text):
                        fb_message(sender_id, "you want a reminder?")
                    else:
                        fb_message(sender_id, "not a reminder")
                    client.run_actions(session_id=sender_id, message=message_text)
                if messaging_event.get("delivery"):
                    pass
                if messaging_event.get("optin"):
                    pass
                if messaging_event.get("postback"):
                    pass
    else:
        return "Recieved different event"
    return "ok", 200


# get the value of the first appearance of that entity
def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def fb_message(sender_id, text):
    # returns the response  back to messenger
    log("sending message back to {recipient}: {text}".format(recipient=sender_id, text=text))

    params = {"access_token": FB_PAGE_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
            "text": text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.5/me/messages",params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send(request, response):
    fb_id = request['session_id']
    text = response['text']
    fb_message(fb_id, "wit: "+ text)

def delete_missing(context, entity):
    if context.get(entity) is not None:
        del context[entity]

def send_reminder(sender_id, reminder_message, delta_time):
    sleep(delta_time)
    fb_message(sender_id, "reminder: "+reminder_message)


def add_reminder(request):
    context = request['context']
    entities = request['entities']
    fb_id = request['session_id']
    context['timezone'] = "Asia/Kolkata"
    reminder_str = first_entity_value(entities, "reminder")
    reminder_time = first_entity_value(entities, "datetime")
    log("reminder_str: " + reminder_str)
    log("reminder_time: " + reminder_time)
    if reminder_time:
        context['reminderTime'] = str(reminder_time)
        delete_missing(context, 'missingTime')
    else:
        context['missingTime'] = True
        delete_missing(context, 'reminderTime')

    if reminder_str:
        context['reminderStr'] = reminder_str
        delete_missing(context, 'missingReminderStr')
    else:
        context['missingReminderStr'] = True
        delete_missing(context, 'reminderStr')
    
    if reminder_time and reminder_str:
        # 2016-12-31T08:12:00.000-08:00
        #date_time = datetime.strptime(reminder_time, "%Y-%m-%dT%H:%M:%S.%f")
        #current_time = datetime.datetime.now()
        #delta_time = (date_time - current_time).total_seconds()
        delta_time = 60
        #job = q.enqueue(send_reminder, fb_id, reminder_str, delta_time)
    return context

def log(message):
    print str(message)
    sys.stdout.flush()

#setup actions
actions = {
    'send': send,
    'addReminder': add_reminder,
}

# setup wit client
client = Wit(access_token=WIT_TOKEN, actions=actions)
#redis_conn = Redis()
#q = Queue(connection=redis_conn)

#scheduler = Scheduler(connection=Redis())

if __name__ == '__main__':
    #run server
    app.run(debug=True)
