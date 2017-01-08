import os
import sys
import json
#import tz
from datetime import datetime

import requests
from flask import Flask, request
from wit import Wit

import wit_functions
import messenger

"""
TODO:
timezone first
based on that do the messages
implement the messaging queues using celery
use rq instead



"""
app = Flask(__name__)



@app.route('/', methods=['GET'])
def verify():
    return verify_fb(request)
    
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




def send(request, response):
    fb_id = request['session_id']
    text = response['text']
    fb_message(fb_id, "wit: "+ text)


def send_reminder(sender_id, reminder_message, delta_time):
    sleep(delta_time)
    fb_message(sender_id, "reminder: "+reminder_message)



def log(message):
    print str(message)
    sys.stdout.flush()




#scheduler = Scheduler(connection=Redis())

if __name__ == '__main__':
    #run server
    app.run(debug=True)
