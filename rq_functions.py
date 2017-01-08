from redis import Redis
from rq import Queue
import messenger
from time import sleep

def add_to_queue(sender_id, reminder_str, delta_time):
    job = q.enqueue(send_reminder_worker, sender_id, reminder_str, delta_time)

def send_reminder_worker(sender_id, reminder_str, delta_time):
   sleep(delta_time)
   fb_message(sender_id, reminder_str)

redis_conn = Redis()
q = Queue(connection=redis_conn)
