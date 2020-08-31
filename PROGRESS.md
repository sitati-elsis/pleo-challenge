In this file, record your progress and think aloud about
the challenge.

## <some title>
I looked over ... and then I wrote down a plan to ...
## Discovery Work

Let me run the containers and investigate how events are generated and stored.

Hmm.. so all events go into an `data/events/inbox/<type>` folder as a json file.

The event json files are prefixed with the event ID which is a UUID. 

The event json files have only one event per file.

The `flush_event` function is the same in both the `cards` and `users` service. 
We could probably extract it to a common utility function/package to standardize it.

The `cards` service seems to write a `__id_counter` randomly everytime the loop sleeps.
This may pose a challenge as its not an event file. 

*We need to validate the kind of files we process*

Hmm... since all the event files are named using the UUID we could write a regex file loader.

The `etl` service literally has no implementation apart from a print hello world. This gives us freedom.

We will probably need to update the dockerfile entrypoint to get the service listening.


## Database Design
There is similarity in the structure of the different event types as seen below.
#### Cards

    {
      "payload": {
        "id": 23,
        "user_id": 884,
        "created_by_name": "Andrew Marks",
        "updated_at": "2020-08-26 11:17:05",
        "created_at": "2020-08-26 11:15:58",
        "active": true
      },
      "metadata": {
        "type": "card",
        "event_at": "2020-08-26 11:17:05",
        "event_id": "0a239cf2-72f8-45ba-8331-f3757dcf67c4"
      }
    }

#### Users
    {
      "metadata": {
        "type": "user",
        "event_at": "2020-08-26 11:15:55",
        "event_id": "0a76c6e0-0cb5-4c2c-a54f-636a25361868"
      },
      "payload": {
        "id": 815,
        "name": "Tasha Houston",
        "address": "4298 Melissa Run\nLawsonfort, CT 17722",
        "job": "Computer games developer",
        "score": 0.8575437451083873
      }
    }
    
How do we store events data efficiently without alot of complexity? I am thinking the 
following structure might work.

Lets just have one table cleverly named `events` with the following structure.

    CREATE TABLE IF NOT EXISTS events
    (
        event_id uuid NOT NULL,
        payload jsonb NOT NULL,
        type text NOT NULL,
        metadata jsonb NOT NULL,
        event_at timestamptz NOT NULL DEFAULT now(),
        UNIQUE (event_id)
    );
    
Lets have a unique constrait on the `event_id` so that we avoid duplicates.

Lets have a `type` and `event_at` field. They may be useful for sharding and lookups later on.


## ETL Implementation

### Event validation

We can probably validate the event data before saving by checking:

1. If the even json filename is a UUID format

2. if it has the following fields.

    - metadata
    - payload
 
 Make sure the table is created when the service spins up
 
 What do we do with the files we have read already? 
 In a better system given more time we could archive it. For for this implementation we will just delete it.
 
 We will keep an open loop that listens for new files in the events folder at intervals to process the files.
 
 A better implementation is to have those files on s3 and use something fancy like an s3 sensor.

 ### Testing that the pipeline works

 List the docker containers to get the container id for the postgress database using the `docker -ps -a` command

 Use the command `docker exec -it <container id> bash` to get a bash shell in the container

 Connect into the database using the `psql -U dwh` command

 Write whatever SQL statements you have in mind to get the records stored in the events table
