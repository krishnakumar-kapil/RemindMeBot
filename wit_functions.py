from wit import Wit
import os
import rq_functions
import sys

import messenger
import time
import datetime
from time import mktime

def send(request, response):
    fb_id = request['session_id']
    text = response['text']
    messenger.fb_message(fb_id, "wit: "+ text)

def receive_test(id, message):
    log("about to run client actions")
    client.run_actions(session_id=id, message=message)

def receive_message(messaging_event):
    #message was sent
    sender_id = messaging_event["sender"]["id"]
    # recipient id is your fb id
    message_text = messaging_event["message"]["text"]
    messenger.fb_message(sender_id, "received message")
    log("message_text_received: "+message_text);
    #get the wit to do stuff
    # if("remind" in message_text):
    #     messenger.fb_message(sender_id, "you want a reminder?")
    # else:
    #     messenger.fb_message(sender_id, "not a reminder")
    client.run_actions(session_id=sender_id, message=message_text)


def add_reminder(request):
    context = request['context']
    entities = request['entities']
    fb_id = request['session_id']
    context['timezone'] = "Asia/Kolkata"
    reminder_str = first_entity_value(entities, "reminder")
    reminder_time = first_entity_value(entities, "datetime")
    log("reminder_str: " + reminder_str)
    log("reminder_time: " + reminder_time)
    log("HELLOOOOOOO")
    log(str(context))
    log(str(entities))
    # if reminder_time:
    #     context['reminderTime'] = str(reminder_time)
    #     delete_missing(context, 'missingTime')
    # else:
    #     context['missingTime'] = True
    #     delete_missing(context, 'reminderTime')
    #
    # if reminder_str:
    #     context['reminderStr'] = reminder_str
    #     delete_missing(context, 'missingReminderStr')
    # else:
    #     context['missingReminderStr'] = True
    #     delete_missing(context, 'reminderStr')

    context['reminderTime'] = str(reminder_time)
    context['reminderStr'] = reminder_str
    log(str(type(reminder_time)))
    if reminder_time and reminder_str:
        # 2016-12-31T08:12:00.000-08:00
        reminderTime = time.strptime(reminder_time[:-6], "%Y-%m-%dT%H:%M:%S.%f")
        log("type of reminder_time" + str(type(reminder_time)))
        #datetime.fromtimestamp(mktime(struct))
        reminderTime = datetime.datetime.fromtimestamp(mktime(reminderTime))
        current_time = datetime.datetime.now()
        delta_time = (reminderTime - current_time).total_seconds()
        #delta_time = 60
        log("adding to queue in:" + str(delta_time))
        rq_functions.add_to_queue(fb_id, "reminder:" + reminder_str, delta_time)
#        job = q.enqueue(send_reminder, fb_id, reminder_str, delta_time)
    return context

def delete_missing(context, entity):
    if context.get(entity) is not None:
        del context[entity]

# get the value of the first appearance of that entity
def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def log(message):
    print str(message)
    sys.stdout.flush()



#setup actions
actions = {
    'send': send,
    'addReminder': add_reminder,
}


WIT_TOKEN = os.environ["WIT_TOKEN"]
client = Wit(access_token=WIT_TOKEN, actions=actions)
