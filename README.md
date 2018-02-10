# SebastianSlackBot


Using the Slack API, I made a bot which will utilize the Archapp app which goes through the EPICS Archiver and pulls PV values for a given start and end time.
If properly used, Sebastian can make sure he has data on your PV

If he can find your PV, you can provide a start and end time, and Sebastian will return with a graph of the PV value (y-axis) vs time (x-axis)

To use Sebastian,

1.) Tag him in Slack as a channel which you invite @Sebastian too, or through the Apps tab

2.) To see if your PV is valid, type:

@Sebastian search <YOUR DESIRED PV>

He will let you know if he has found any data regarding your query


3.) Follow this format, it is very strict since the string formatting will throw him off

Example command:

@Sebastian find <YOUR DESIRED PV HERE> start=day,hour,min,sec end=day,hour,min,sec

the start= and end = is required.

You cannot omit any of the day-hour-min-sec. If it is 0, make sure you put the 0 there

For example if you wanted the stats for 30 seconds ago

@Sebastian find <YOUR PV> start=0,0,30,0 end-0,0,0,0

Another example would be from 10 days ago to 5 days ago

@Sebastian find <YOUR PV> start=10,3,54,0 end=5,3,54,0


