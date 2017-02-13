from redis import Redis
from rq import Queue
from time import sleep
import messenger

def add_to_queue(sender_id, reminder_str, delta_time):
    job = q.enqueue(send_reminder_worker, sender_id, reminder_str, delta_time)

def send_reminder_worker(sender_id, reminder_str, delta_time):
    sleep(float(delta_time))
    print("HELLOOOOOO")
    messenger.fb_message(sender_id, reminder_str)

redis_conn = Redis()
q = Queue(connection=redis_conn)
