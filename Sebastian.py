import sys
sys.path.append('/reg/neh/home5/yashas/miniconda3/lib/python3.6/site-packages')
import json, os, time, re, xarray, simplejson, requests
from slackclient import SlackClient
from archapp.interactive import EpicsArchive
import pandas as pd
import matplotlib.pyplot as plt

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

#instantiate EpicsArchiver
arch = EpicsArchive(hostname="pscaa01-dev")

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
MAIN_COMMAND = "find"
MENTION_REGEX = "^<@(|[WU].+)>(.*)"
HELP_COMMAND = "help"
SEARCH_COMMAND = "search"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot
        commands. If a bot command is found, this function returns a tuple
        of command and channel.If its not found, then this function returns
        None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message
        text and returns the user ID which was mentioned. If there is no
        direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """

#HELP command describes how to best utilize Sebastian

    if command.startswith(HELP_COMMAND):
        """
        The 'help' command will allow users to query the Sebastian bot to
        understand his functionality. Sebastian's response will provide
        detailed instructions on how to properly retrieve a graph of a PV
        of your choice.
        """
        default_response = "I have 2 functions. I can 'search' if I have data on your PV or I can 'find' data on your PV that you know exists.\n Let's go through 'search' first.\n By simply typing in 'search YOURPVHERE', I will be able to tell you if I have data for your specified PV. Simple as that.\n For example: 'search GDET:FEE1:241:ENRC' \n The 'find' command is a little tricker, since you will have to follow a specific format. \n The format is as follows: ' find desiredPV start=day,hour,min,sec end=day,hour,min,sec'. The end date is optional.\n When asking me a query, do not omit any of the values from start/end. If it is zero, put the zero there. Let's say you want a graph of the PV values for the last 2 days 5 hours and 27 minutes ago.\n Your command should look like - 'find GDET:FEE1:241:ENRC start=2,5,27,0'. Do NOT omit any values in start/end"
    
        slack_client.api_call("chat.postMessage", channel=channel, text=default_response)

#SEARCH command will see if PV is even valid

    if command.startswith(SEARCH_COMMAND):

        try:
            split = command.split()
            pv = split[1]
            getPV = arch.get(pv, xarray=True, start=0, end=0.00005)
        
        except IndexError:
            response = "Please provide a proper input when using this command"
            slack_client.api_call("chat.postMessage",channel=channel,text=response)
            return

        try:
            array = getPV[pv]
            response = "I got some data on that PV, use the 'find' command and input some times. Back to hockey"

        except KeyError:
            response = "I don't have any information regarding that PV, please try again."

        except IndexError:
            response = "Please only input the PV value in your query"

        slack_client.api_call("chat.postMessage",channel=channel,text=response)


#FIND command will do the real work

    if command.startswith(MAIN_COMMAND):
        
        #This is to use archapp to extract data and then set up plot with PV value vs date
        split = command.split()
        pv = split[1]
        start = split[2]
        
        try:
            end = split[3]
        except IndexError:
            end = None
  
        if start.startswith("start="):
            start1=start.replace('start=', ' ')
            start2=start1.replace(',', ' ')
            start3 = start2.split()

            try:
                startDay = float(start3[0]) * 1
                startHour = float(start3[1])
                decSHour = startHour/24 
                startMin = float(start3[2])
                decSMin = ((startMin/60)/24)
                startSec = float(start3[3])
                decSSec = (((startSec/60)/60)/24)
                stDec = startDay + decSHour + decSMin + decSSec
                
                response = "Looks like your start times check out, you start time is %s day(s)" % stDec
                slack_client.api_call("chat.postMessage",channel=channel,text=response)

            except IndexError:
                response = "Make sure your query includes start=a,b,c,d. a = days, b = hours, c = minutes, d = seconds. If you do not care about a value, please place a 0 there. Don't be lazy like a Canadian"
                slack_client.api_call("chat.postMessage",channel=channel,text=response)
                return

            except ValueError:
                response = "Please enter a number for your time values"
                slack_client.api_call("chat.postMessage",channel=channel,text=response)
                return

        try:
            if end.startswith("end="):
                end1=end.replace('end=', ' ')
                end2=end1.replace(',', ' ')
                end3 = end2.split()
                endDay = float(end3[0]) * 1
                endHour = float(end3[1])
                decHour = endHour/24
                endMin = float(end3[2])
                decMin = ((endMin/60)/24)
                endSec = float(end3[3])
                decSec = (((endSec/60)/60)/24)
                etDec = endDay + decHour + decMin + decSec

                response = "Looks like your end times check out, you end time is %s day(s)" % (etDec)
                slack_client.api_call("chat.postMessage",channel=channel,text=response)

        except IndexError:
            response = "Make sure your query includes end=a,b,c,d. a = days, b = hours, c = minutes, d = seconds. If you do not care about a time value, please place a 0 there. Don't be lazy like a Canadian"
            slack_client.api_call("chat.postMessage",channel=channel,text=response)
            return

        except ValueError:
            response = "Please enter a number for your time values"
            slack_client.api_call("chat.postMessage",channel=channel,text=response)
            return
        
        except AttributeError:
            print("No End value specififed")

        response = "Your time inputs check out - I'll be back with your plot after validating your PV. If you don't hear from me for a few seconds, do not worry, I'm making your graph."
        slack_client.api_call("chat.postMessage",channel=channel,text=response)
       
        try:
            getPV = arch.get(pv, xarray=True, start=stDec, end=etDec)
            print("arch.get(%s, xarray=True, start=%s, end=%s)" % (pv, stDec, etDec))

        except UnboundLocalError:
           getPV = arch.get(pv, xarray=True, start=stDec)
           print("arch.get(%s, xarray=True, start=%s)" % (pv, stDec))

        try:
            array = getPV[pv]

        except KeyError:
            response = "Invalid PV, please try your PV with my 'search' command to make sure I have data on your PV"
            slack_client.api_call("chat.postMessage",channel=channel,text=response)
            return

        response = "Graph coming soon. I accept all forms of maple syrup as a thank you"
        slack_client.api_call("chat.postMessage",channel=channel,text=response)
        panda = array.to_pandas()
        transpose = panda.transpose()
        vals = transpose.get('vals')

        #This is setting up parameters for the graph to return
        sortVals = vals.sort_values()
        minVal = sortVals[0]
        lenOfVals = len(vals)
        maxVal = sortVals[(lenOfVals-1)]
        plt.figure(figsize=(12,7))
        plot = plt.plot(vals)
        plt.ylabel(pv)
        plt.xlabel('Time')
        plt.ylim([(minVal-(0.1*minVal)),(maxVal+(0.1*maxVal))])
        

        #Saving plot and path to plot
        try:
            graph = plt.savefig('/reg/neh/home/yashas/slackbot/archapp/lib/%s.png'%(pv))
            pathToGraph = '/reg/neh/home/yashas/slackbot/archapp/lib/%s.png'%(pv)
            print("success")
   
        except UnboundLocalError:
            graph = plt.savefig('/reg/neh/home/yashas/slackbot/archapp/lib/%s.png'%(pv))
            pathToGraph = '/reg/neh/home/yashas/slackbot/archapp/lib/%s.png'%(pv)
            print("success")


        #slackAPI not working, works perfectly through requests module
        r = requests.post('https://slack.com/api/files.upload',
                        data={'token': (os.environ.get('SLACK_BOT_TOKEN')), 'channels':channel,
                              'title':'%s%s.png'%(pv,time)},
                        files={'file': open(pathToGraph,'rb')}) 



    if command.startswith(HELP_COMMAND) == False and command.startswith(SEARCH_COMMAND) == False and command.startswith(MAIN_COMMAND) == False:
        response = "Dilly Dilly. Please type in 'help' to see how I may assist you today"
        slack_client.api_call("chat.postMessage",channel=channel,text=response)



if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)

    else:
        print("Connection failed. Exception traceback printed above.")
