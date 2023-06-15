
# Author: zksx
# Version 0.0

import os
import time
import sys
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from commands import Message
from commands import Command
import constants


def command_check(msg: Message, youtube, livechat_id: str) -> None:
    """Checks msg to seee if it is a valid cmd by owner/mod

        Args:
            youtube - socket object
            livechat_id - string of live chat id

        Returns: livechatId
    """

    # check if the message is from a user who can do commands
    has_control = get_permissions(msg)

    # check if msg is from owner or mod
    if has_control:

        # check if they are running a command
        if msg.text[0] == '!' and len(msg.text) > 1:

            # make a command class
            cmd = Command()

            # fill command with data
            cmd.load_cmd(msg, youtube, livechat_id)

            # if command is valid
            if cmd.is_valid:

                # execute command
                cmd.execute()

            # otherwise command isn't valid
            else:

                error_str = "Not a valid action or doesn't have enough \
                information"

                cmd.send_err(error_str)


def get_creds():
    """ Gets the creds to login to google account to be used the chat bot.

        Returns:
            Creds
    """

    credentials = None

    # check if a token exists
    if os.path.exists("token.pickle"):
        print("loading Credintials from file...")

        # store the token.pickl into token. "rb" is used here since
        # token.pickle is written in binary
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available,
    # then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                scopes=[
                    "https://www.googleapis.com/auth/youtube.force-ssl"
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')

            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    return credentials

def get_live_chat_id(youtube, video_id: str) -> str:
    """Gets video id in order to find the live chat id of said video.

        Args:
            youtube - socket object
            video_id - id of the video we're trying to get the chat live id for

        Returns:
            live_chat_id
    """

    # use channels id to search for live event types.
    # QUOTA COST = 1
    request = youtube.videos().list(
        part="liveStreamingDetails",
        id=f"{video_id}",
        maxResults=1
    )

    # sending request and getting response
    v_l_response = request.execute()

    items = v_l_response["items"]

    # save livechat_id
    live_chat_id = items[0]["liveStreamingDetails"]["activeLiveChatId"]

    # return video id
    return live_chat_id


def get_offline_at(response: dict):
    """ Returns offlineAt from youtube response"""
    return response["offlineAt"]


def get_next_pt(response: dict) -> int:
    """ Returns nextPageToken from youtube response"""
    return response["nextPageToken"]


def get_permissions(msg) -> bool:
    """Checks to see if the message sent by the user has permissions

        Args:
            msg - youtube chat msg

        Returns:
            bool - if the user
    """

    if msg.is_mod or msg.is_owner:
        return True

    return False


def get_stream_status(lcm_l_response: dict) -> bool:
    """Checks if the stream is still live or not

        Args:
            response - live chat message list response object from 
                        Youtube API

        Returns: if stream is live or not
    """
    # TODO this seems BAD. The program should find if the reponse contains
    # "offlineAt" a different way that doesn't depend on error handling

    # try to get the offlineAt property
    try:
        get_offline_at(lcm_l_response)
        return False

    # if an error occurs that means there is not offlineAt property
    # and the stream is still live
    except Exception as e:
        print(e)
        return True


def get_vid_id(youtube, channel_id) -> str:
    """Attempts to find video id of  a live video of said youtube channel.

        Args:
            youtube

        Returns:
            video id of live stream
    """

    # use channels id to search for live event types.
    # QUOTA COST = 100
    input("You're about to search, press enter to continue: ")

    request = youtube.search().list(
        part="snippet",
        channelId=f"{channel_id}",
        eventType="live",
        maxResults=1,
        type="video"
    )

    # sending request and getting response
    s_l_response = request.execute()

    # save vid_id
    vid_id = s_l_response["items"][0]["id"]["videoId"]

    # return video id
    return vid_id


def get_wait_time(lcm_l_response: dict) -> int:
    "Finds the pollingIntervalMillis"

    return lcm_l_response["pollingIntervalMillis"]


def look_for_live_event(youtube, channel_id) -> str:
    """Continous looks for a live event until one is found

        Args:
            youtube - sokcet object

        Returns:
            livechatId
    """

    # variables
    invalid_chat_id = True

    # look for live chat id
    while invalid_chat_id:

        # attempt to find valid livechat id
        try:
            # find vid_id
            vid_id = get_vid_id(youtube, channel_id)

            # use video id to find livechatID
            live_chat_id = get_live_chat_id(youtube, vid_id)

            # set invalid chat id to false
            invalid_chat_id = False

            print("live chat ID found: " + live_chat_id)

            return live_chat_id

        # otherwise livechat id was not found
        except Exception as e:
            print("No id, waiting 5 mins")
            # test what e is, this can be used for error handling
            # print(e)
            # wait 5 minutes before retrying
            time.sleep(constants.FIVE_MINS)


def main() -> None:
    """Gets login creds, builds youtube socket, and starts nuzlocke loop

        Args:
            youtube - socket object

        Returns:
            None
    """
    
    # check for channel_id in args
    try:
        channel_id = sys.argv[1]

        # get oauth log in creds
        credentials = get_creds()

        # build youtube object
        youtube = build("youtube", "v3", credentials=credentials)

        # make msg object
        nuzlocke_driver(youtube, channel_id)

        # close connection
        youtube.close()

    except IndexError:
        print("NO CHANNEL ID GIVEN")

    except Exception as e:
        print(e)

    print("SHUTTING DOWN")


def nuzlocke_driver(youtube, channel_id) -> None:
    """Handles the main loop for checking youtube msgs

        Args:
            youtube - socket object
            channel_id - ID of channel to find live streams on

        Returns:
            None
    """

    # variables
    next_page_token = ""
    wait_time = 0
    livechat_id = None
    done = False

    # while the program should be running
    while not done:

        # try to set the livechat_id using argv
        try:

            # set live_chat id to the argument passed in
            livechat_id = sys.argv[2]

        # otherwise search for one
        except Exception as e:
            # find the live stream id
            livechat_id = look_for_live_event(youtube, channel_id)

        print("Waiting for messages...")

        streaming = True

        # while livestream is alive
        while streaming:

            # making request request for chat messages
            # QUOTA COST = 20
            request = youtube.liveChatMessages().list(

                liveChatId=f"{livechat_id}",
                part="snippet, authorDetails",
                pageToken=next_page_token
            )

            # sending request and getting response
            lcm_l_response = request.execute()

            # get offline response
            streaming = get_stream_status(lcm_l_response)

            # save next page token
            # (used to gather chat messages from last gathered message)
            next_page_token = get_next_pt(lcm_l_response)

            # save pollingIntervalMillis
            # ( used to wait until captureing next page)
            poll_int_mils = get_wait_time(lcm_l_response)

            wait_time = poll_int_mils / constants.MILL_CONVER

            parse_live_chat(lcm_l_response, youtube, livechat_id)

            # wait the number poll interval time
            time.sleep(wait_time)

            # if the stream is dead wait one minute, this is to avoid a
            # spam loop of finding the livechatID but the streeam is
            # offline. This Quota cost is insane
            if not streaming:
                print("Stream is offline, waiting 5 mins")
                time.sleep(constants.FIVE_MINS)


def parse_live_chat(response: dict, youtube, livechat_id: str) -> None:
    """Makes message object prints messages from authors, calls the cmd func

        Args:
            response - response object from Youtube API

        Returns:
            None
    """

    items = response["items"]

    # for the items in the reesponsee
    for item in items:

        # make msg object
        msg = Message()

        # fill message with text from user
        msg.load_msg(item)

        # print the display message
        print(msg.author_name + ": " + msg.text)

        # check if the msg is a command
        command_check(msg, youtube, livechat_id)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
