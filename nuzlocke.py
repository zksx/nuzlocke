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

def has_action(msg):
    return msg.text[0] == '!' and len(msg.text) > 1


def try_command(msg: Message, youtube, livechat_id: str) -> None:
    """Checks msg to seee if it is a valid cmd by owner/mod"""

    # check if the message is from a user who can do commands
    from_mod_or_owner = get_permissions(msg)

    if from_mod_or_owner:

        contains_action = has_action(msg)

        if contains_action:

            cmd = Command()
            cmd.load_cmd(msg, youtube, livechat_id)

            if cmd.is_valid:
                cmd.execute()

            else:
                error_str = "Not a valid action or doesn't have enough \
                information"

                cmd.send_err(error_str)

def get_creds() -> str:
    """ Gets the creds to login to google account to be used the chat bot."""

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
    """Gets video id in order to find the live chat id of said video"""

    request = youtube.videos().list(
        part="liveStreamingDetails",
        id=f"{video_id}",
        maxResults=1
    )

    video_list_resp = request.execute()

    items = video_list_resp["items"]

    live_chat_id = items[0]["liveStreamingDetails"]["activeLiveChatId"]

    return live_chat_id


def get_offline_at(response: dict):
    return response["offlineAt"]


def get_next_pt(response: dict) -> int:
    return response["nextPageToken"]


def get_permissions(msg) -> bool:
    """Checks to see if the message sent by the user has permissions"""

    if msg.is_mod or msg.is_owner:
        return True

    return False


def is_stream_alive(livechatmsg_list_resp: dict) -> bool:
    """Checks if the stream is still live or not"""
    # TODO this seems BAD. The program should find if the reponse contains
    # "offlineAt" a different way that doesn't depend on error handling

    # try to get the offlineAt property
    try:
        get_offline_at(livechatmsg_list_resp)
        return False
    
    except KeyError as e:
        return True

    # if an error occurs that means there is not offlineAt property
    # and the stream is still live
    except Exception as e:
        print(e)
        return True


def get_vid_id(youtube, channel_id) -> str:
    """Attempts to find video id of  a live video of said youtube channel."""

    input("You're about to search, press enter to continue: ")

    request = youtube.search().list(
        part="snippet",
        channelId=f"{channel_id}",
        eventType="live",
        maxResults=1,
        type="video"
    )

    search_list_resp = request.execute()

    vid_id = search_list_resp["items"][0]["id"]["videoId"]

    return vid_id


def get_wait_time(livechatmsg_list_resp: dict) -> int:
    return livechatmsg_list_resp["pollingIntervalMillis"]


def look_for_live_event(youtube, channel_id) -> str:
    """Continously looks for a live event until one is found

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
            time.sleep(constants.FIVE_MINS)


def main() -> None:
    """Gets login creds, builds youtube socket, and starts nuzlocke loop"""

    argv_len = len(sys.argv)
    
    # check for channel_id in args
    if argv_len > 1:
        channel_id = sys.argv[1]

        # get oauth log in creds
        credentials = get_creds()

        youtube = build("youtube", "v3", credentials=credentials)

        nuzlocke_driver(youtube, channel_id)

        # close connection
        youtube.close()

    else:
        print("NO CHANNEL ID GIVEN")

    print("SHUTTING DOWN")


def nuzlocke_driver(youtube, channel_id) -> None:
    """Handles the main loop for checking youtube msgs"""

    # variables
    next_page_token = ""
    wait_time = 0
    livechat_id = None
    done = False
    argv_len = len(sys.argv)

    # while the program should be running
    while not done:

        # try to set the livechat_id using argv
        if argv_len > 2:

            livechat_id = sys.argv[2]

        # otherwise search for one
        else:
            # find the live stream id
            livechat_id = look_for_live_event(youtube, channel_id)

        print("Waiting for messages...")

        streaming = True

        # while livestream is alive
        while streaming:

            request = youtube.liveChatMessages().list(

                liveChatId=f"{livechat_id}",
                part="snippet, authorDetails",
                pageToken=next_page_token
            )

            livechatmsg_list_resp = request.execute()

            # get offline response
            streaming = is_stream_alive(livechatmsg_list_resp)

            # save next page token
            # (used to gather chat messages from last gathered message)
            next_page_token = get_next_pt(livechatmsg_list_resp)

            poll_int_mils = get_wait_time(livechatmsg_list_resp)

            wait_time = poll_int_mils / constants.MILL_CONVER

            parse_live_chat(livechatmsg_list_resp, youtube, livechat_id)

            # wait the number poll interval time
            time.sleep(wait_time)

            if not streaming:
                print("Stream is offline, waiting 5 mins")
                time.sleep(constants.FIVE_MINS)


def parse_live_chat(response: dict, youtube, livechat_id: str) -> None:
    """Makes message object prints messages from authors, calls the cmd func"""

    for item in response["items"]:

        msg = Message()

        # fill message with text from user
        msg.load_msg(item)

        print(msg.author_name + ": " + msg.text)

        # try to execute a command if possiblee
        try_command(msg, youtube, livechat_id)

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
