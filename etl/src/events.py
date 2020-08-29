import os
import re
import fastjsonschema
import json
from schema import bulk_insert
from logger import logger

EVENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "payload": {
            "type": "object"
        },
        "metadata": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string"
                },
                "event_at": {
                    "type": "string"
                },
                "event_id": {
                    "type": "string",
                    "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
                },
            },
            "required": [
                "type",
                "event_at",
                "event_id",
            ]
        }
    },
    "required": [
        "payload",
        "metadata"
    ]
}

UUID_ALL_PATTERN = re.compile(
    (
            '[a-f0-9]{8}-' +
            '[a-f0-9]{4}-' +
            '[1-5]' + '[a-f0-9]{3}-' +
            '[89ab][a-f0-9]{3}-' +
            '[a-f0-9]{12}.json$'
    ),
    re.IGNORECASE
)

event_schema_validator_func = fastjsonschema.compile(EVENT_SCHEMA)


def get_list_of_event_json_files(events_dir):
    files = [os.path.join(events_dir, f) for f in os.listdir(events_dir) if UUID_ALL_PATTERN.match(f)]
    return files


def archive_event_files(event_files):
    for event_file in event_files:
        if os.path.exists(event_file):
            try:
                os.remove(event_file)
            except OSError:
                pass


def consume_events(event_type, events_dir):
    events_dir = os.path.join(events_dir, event_type)
    event_files = get_list_of_event_json_files(events_dir)
    events = []
    for event_file in event_files:
        with open(event_file) as fp:
            try:
                data = event_schema_validator_func(json.load(fp))
                data['event_id'] = data['metadata']['event_id']
                data['event_at'] = data['metadata']['event_at']
                data['type'] = data['metadata']['type']
                data['meta_data'] = data['metadata']
                events.append(data)
            except fastjsonschema.exceptions.JsonSchemaException as e:
                logger.error(f"Invalid JSON schema found in events file {event_file}")
                logger.error(e)
            except Exception as e:
                logger.error(e)
    if events:
        try:
            logger.info(f"Ingesting {len(events)} {event_type} events")
            bulk_insert(events)
            logger.info(f"Ingested {len(events)} {event_type} events")
        except Exception as e:
            logger.error(e)
        archive_event_files(event_files)
