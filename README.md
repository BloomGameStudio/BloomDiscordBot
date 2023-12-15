# BloomDiscordBot

# Help:

You can type ```$bot_help``` to get details about what commands can be used, along with a brief description of them

# Events:

When a person creates an event within Blooms Discord server, there will initially be a one hour delay from the time of creation to when the details of the event are posted. This will allow the person sometime to make changes to the details, timing and so on.

There is a daily scheduled task that will identify events starting within the next 24 hours. If any are detected everyone is informed of the events details in a Discord message.

Events can also be deleted through a command, detailed below.

# Commands:

The following commands can be used to manage, and list events.
All commands start with: $

**List Events:**

```
$list_events
```

**Example:**

```
$list_events
```

**Response:**

```
🗓️ All Events🗓️ 

🌺 Scrutinizer Game night🌺 
event_id: 1180231420476670043
Description: 

🌺 Modular Mesh Architecture🌺 
event_id: 1184322631692980325
Description:
```

**Delete Events:**

```
$delet_eevent <event_id>
```

**Example:**

```
$delete_event 1179242504395165748
```

**Response:**

```
Event with ID 1179242504395165748 has been deleted.
```



