import requests
import os
#from flask import Flask, request

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

def verify_fb(request):
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == FB_VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Sup", 200

def log(message):
    print str(message)
    sys.stdout.flush()



FB_PAGE_TOKEN = os.environ["FB_PAGE_TOKEN"]
FB_VERIFY_TOKEN = os.environ["FB_VERIFY_TOKEN"]
