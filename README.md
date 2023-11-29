# BloomDiscordBot

# Events:

When a person creates an event within Blooms Discord server, there will initially be a one hour delay from the time of creation to when the details of the event are posted. This will allow the person sometime to make changes to the details, timing and so on.

There is a daily scheduled task that will identify events starting within the next 24 hours. If any are detected everyone is informed of the events details in a Discord message.

Events can also be deleted through a command, detailed below.

# Commands:

The following commands can be used to manage, and list events.
All commands start with: !

**List Events:**

```
!listevents
```

**Example:**

```
!listevents
```

**Response:**

```
All Events:
Event Name: cvbncvbncvbn
Event ID: 1178917740216594432
Event Start Time: November 30, 2023 4:00 PM
Event Description: 
Event Interested: 0
```

**Delete Events:**

```
!deleteevent <event_id>
```

**Example:**

```
!deleteevent 1179242504395165748
```

**Response:**

```
Event with ID 1179242504395165748 has been deleted.
```



