from schema import create_events_table
from events import consume_events

import time
import os

EVENTS_DIR = os.getenv('EVENTS_DIR', './events')

EVENT_TYPES = ['cards', 'users']

if __name__ == "__main__":
    create_events_table()
    while True:
        for event_type in EVENT_TYPES:
            consume_events(event_type=event_type, events_dir=EVENTS_DIR)
        time.sleep(10)
