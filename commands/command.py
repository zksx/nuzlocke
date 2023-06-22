from typing import *
from pathlib import Path

import sqlite3

from .valid_commands import VALID_CMDS
from .message import Message

db_pth = Path("databases/nuzlocke.db")

class Command:
    """ Command class

    Args:
        self -- NuzlockeUser class
        user_name -- display name associted with the user
        poke_name -- the pokemon that is asscoiteed with the user
        channel_id -- channel id that is asscoited with the user

    Returns: N/A
    """
    def __init__(self,
                 action: str = "",
                 author_name: str = "",
                 is_valid: bool = False,
                 youtube=None,
                 live_chat_id: str = "",
                 users: list = []):

        self.action = action
        self.author_name = author_name
        self.is_valid = is_valid
        self.youtube = youtube
        self.live_chat_id = live_chat_id
        self.users = users

    def insert_user_data_into_db(self, cursor, user):
        # insert the name and nickname into the database
        cursor.execute("INSERT INTO users \
                        VALUES (?, ?, 'false', 'true', ?, ?, '' )",
                        (user.user_name, user.poke_name,
                        self.author_name, user.channel_id))

    def assign(self, user, cursor: sqlite3.Cursor) -> None:
        """Inserts user with asscoiated poke name in database"""

        # variables
        unique_channel = self.useable_channel(user.channel_id, cursor)
        unique_pokemon = self.useable_pokemon(user.poke_name, cursor)
        is_real_pokemon = self.is_real_pokemon(user.poke_name)

        if unique_channel and unique_pokemon and is_real_pokemon:

            self.insert_user_data_into_db(cursor)
            self.send_suc()

        elif not unique_channel:

            error_str = f"This channel id has already been used"
            self.send_err(error_str)

        elif not unique_pokemon:

            error_str = f"This pokemon has already been used in this run"
            self.send_err(error_str)

        # otherwise the given pokemon name was not an actual pokemon
        else:

            error_str = "something went wrong"
            self.send_err(error_str)

    def execute(self) -> None:
        """Executes command, mainly sql commands for the database"""

        conn = sqlite3.connect(db_pth)
        cursor = conn.cursor()

        # check for each command
        match self.action:
            case "!assign":
                self.assign(self.users[0], cursor)

            case "!release":
                self.release(self.users[0], cursor)

            case "!newrun":
                self.new_run(self.users, cursor)

            case "!victory":
                self.victory(self.users, cursor)

            case _:
                print("command not found")

        conn.commit()
        self.show_data(cursor)

    def get_channel_id(self, action: str, cmd_text_arr: list[str]) -> str:

        cmd_len = len(cmd_text_arr)
        channel_id_index = cmd_len - 1
        channel_id = ""

        if action == "!assign":

            channel_id = cmd_text_arr[channel_id_index]

            return channel_id

        return channel_id

    def get_poke_name_from_command(self, action: str, cmd_text_arr: list[str]) -> str:
        """Gets the poke_name from the command the user entered via youtube chat
            if there is a poke_name."""
        
        cmd_len = len(cmd_text_arr)
        index = 0
        poke_name = ""
        second_to_last_index = cmd_len - 2
        last_index = cmd_len - 1

        if action == "!assign":

            # start index at 1 to skip the action text
            index = 1

            while index < last_index:

                poke_name += cmd_text_arr[index]

                if index < second_to_last_index:

                    poke_name += ' '

                index += 1

        elif action == "!release":

            poke_name = cmd_text_arr[last_index]

            return poke_name

        return poke_name

    def get_user_name_from_channel_id(youtube, channel_id: str) -> str:
            
            # make a request for the users display name
            request = youtube.channels().list(
                part="snippet",
                id=f"{channel_id}"
            )
            response = request.execute()

            user_name = response["items"][0]["snippet"]["title"]

            return user_name
    
    def get_user_data_from_poke_name(cursor, poke_name):

        # get user data
        cursor.execute("SELECT channel_id, poke_name, user_name \
                        FROM users \
                        WHERE poke_name = ? \
                        AND in_this_run='true'",
                        (poke_name,))

        user_data_arr = cursor.fetchone()

        return user_data_arr
    
    def get_unbanned_users_in_this_run(cursor):
        # search the database returning all banned users with their
        # user_name, and ban_id
        cursor.execute("SELECT user_name, ban_id \
                        FROM users \
                        WHERE banned='true'")

        users = cursor.fetchall()

        return users
    
    def convert_user_data_to_user_array(self, users_data):
        
        users_arr = []

        for user_data in users_data:

            channel_id = user_data[0]
            poke_name = users_data[1]
            user_name = users_data[2]
            ban_id = users_data[3]

            user = self.NuzlockeUser(user_name, poke_name, channel_id, ban_id)
            users_arr.append(user)

        return users_arr
    
    def get_banned_users_data(cursor):
            
        cursor.execute("SELECT user_name, ban_id \
                        FROM users \
                        WHERE banned='true'")

        users_data = cursor.fetchall()

        return users_data


    def get_users(self, action: str, poke_name: str, channel_id: str):
        """ Gets the users targeted by the command """

        users_arr = []
        user_name = ""

        conn = sqlite3.connect(db_pth)
        cursor = conn.cursor()

        # check if the action is assign
        if action == "!assign":

            user_name = self.get_user_name_from_channel_id(self.youtube, channel_id, poke_name)
            user = [self.NuzlockeUser(user_name, poke_name, channel_id)]

            return user

        # otherwise check if the action is !release
        elif action == "!release":

            user_data_arr = self.get_user_data_from_poke_name(cursor, poke_name)

            # if the user data isn't empty fill it
            if user_data_arr is not None:

                channel_id = user_data_arr[0]
                poke_name = user_data_arr[1]
                user_name = user_data_arr[2]
                ban_id = user_data_arr[3]

            user = [self.NuzlockeUser(user_name, poke_name, channel_id, ban_id)]

            return user

        # otherwise check the action is !newrun
        elif action == "!newrun":

            users_data = self.get_unbanned_users_in_this_run

            users_arr = self.convert_user_data_to_user_array(users_data)

            return users_arr

        # otherwise the action is !victory
        else:

            users_data = self.get_banned_users_data(cursor)

            users_arr = self.convert_user_data_to_user_array(users_data)

            return users_arr
        
    def ban_users_and_remove_from_this_run(cursor):

        # Update the database and seet the users in
        # this run to be banned and not in the run anymore.
        cursor.execute("UPDATE users SET banned='true', in_this_run='false' \
                        WHERE in_this_run='true'")


    def new_run(self, users, cursor: sqlite3.Cursor) -> None:
        """Sets all pokemon in the run to the banned status.
                Also bans all the users in youtube chat """

        for user in users:

            # ban this user
            self.release(user, cursor)

        self.ban_users_and_remove_from_this_run()

        self.send_suc()

    def get_all_pokemon_names(cursor):

        cursor.execute("SELECT name FROM pokemon;")
        all_pokemon_names = cursor.fetchall()

        return all_pokemon_names
    
    def lowercase_and_strip_white_space(string):

        new_string = string.lower()
        new_string = string.replace(" ", "")

        return new_string

    def is_is_real_pokemon(self, user_poke_name: str) -> bool:
        """Returns if the pokemon is a real pokemon"""

        conn = sqlite3.connect(db_pth)
        cursor = conn.cursor()

        poke_names = self.get_all_pokemon_names(cursor)

        tmp_poke_name = self.lowercase_and_strip_white_space(user_poke_name)

        for poke_name in poke_names:

            # save the og pokemon name with spaces/caps
            orignial_name = poke_name[0]

            # assign the one str in the arr poke_name
            # to poke_name for ease
            poke_name = poke_name[0]
            poke_name = self.lowercase_and_strip_white_space(poke_name)

            print(tmp_poke_name + ": " + poke_name)

            # check if the poke_name is in the database
            if tmp_poke_name == poke_name:

                # set the cmds pokee_name to the pokemon name
                # with white space and caps
                user_poke_name = orignial_name

                return True

        return False
    
    def get_user_data_from_poke_name(poke_name, cursor):
        cursor.execute("SELECT user_name From users WHERE \
                poke_name = ? \
                AND in_this_run='true'",
                (poke_name,))

        user_name = cursor.fetchone()

        return user_name
    
    def get_ban_id(self, channel_id, live_chat_id, youtube):
            
            # get ban id for user
            request = youtube.liveChatBans().insert(
                part="snippet",
                body={
                    "snippet":
                        {
                            "liveChatId": f"{live_chat_id}",
                            "type": "permanent",
                            "bannedUserDetails":
                            {
                                "channelId": f"{channel_id}"
                            }
                        }
                    }
            )
            response = request.execute()

            ban_id = response["id"]

            return ban_id
    
    def ban_users_in_db(cursor, poke_name, channel_id):
        cursor.execute("UPDATE users\
                        SET banned='true' \
                        WHERE poke_name = ? \
                        AND channel_id = ?",
                        (poke_name, channel_id))
        
    def update_ban_id_for_users_in_db(cursor, ban_id, channel_id):
        cursor.execute("UPDATE users SET \
                        ban_id = ? \
                        WHERE channel_id = ?",
                        (ban_id, channel_id))

    def release(self, user, cursor: sqlite3.Cursor) -> None:
        """To be used when a pokemon is released in the wild.
            This bans the users assigned to that pokemon"""
        # find out if the pokemon thee user is searching for is real
        is_real_pokemon = self.is_real_pokemon(user.poke_name)

        user_name = self.get_user_name_from_poke_name(user.poke_name)

        # if there is a result then execute a release on the pokemon
        if user_name is not None and is_real_pokemon:

            self.ban_users_in_db(cursor, user.poke_name, user.channel_id)

            ban_id = self.get_ban_id(self.channel_id, self.live_chat_id, self.youtube)

            self.update_ban_id_for_users_in_db(ban_id, user.channel_id)

            self.send_suc()

        else:
            err_str = "Not a valid pokemon to release"
            self.send_err(err_str)

    def send_err(self, err_str: str) -> None:
        """Sends an error message via chat to the author of the command"""

        request = self.youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet":
                    {
                        "liveChatId": f"{self.live_chat_id}",
                        "type": "textMessageEvent",
                        "textMessageDetails":
                        {
                            "messageText": f"@{self.author_name} Error: \
                                                                    {err_str}"
                        }
                    }
                }
            )

        # send message
        request.execute()

    def send_suc(self) -> None:
        """ Sends an success message via chat to the author of the command"""

        request = self.youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": f"{self.live_chat_id}",
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": f"@{self.author_name} success"
                    }
                }
            })

        request.execute()

    def set_cmd(self, msg_text_arr: list[str]) -> None:
        """ Sets all the cmd attributes from the msg"""

        text_arr_len = len(msg_text_arr)

        self.action = msg_text_arr[0]

        # use the actions to determine the length
        if self.action == "!assign":
            poke_name_length = text_arr_len - 1

        elif self.action == "!release":
            poke_name_length = text_arr_len

        if text_arr_len > 1:

            # index at 1 to skip the action command beiong assigned
            i = 1

            # assign all the indexs between the first and last to
            # the poke_name
            while i < poke_name_length:

                # assign indexed text to poke_name
                self.poke_name += msg_text_arr[i]

                # add a space inbetween while if the pokemons name
                # and not at the end of their name.
                # i.e: "Roaring Moon", not "Roaring Moon "
                if i < text_arr_len - 2:

                    # add space
                    self.poke_name += ' '

                i += 1

            if text_arr_len > 2:

                # assign the channel id to the command channel_id
                self.channel_id = msg_text_arr[text_arr_len - 1]

    def load_cmd(self, msg: Message, youtube, live_chat_id: str) -> None:
        """ Sets all the cmd attributes from the msg"""

        self.author_name = msg.author_name
        self.set_youtube(youtube)
        self.set_live_chat_id(live_chat_id)

        # split the text into an array
        cmd_text_arr = self.convert_to_array(msg.text)

        # set the action to be executed
        self.action = cmd_text_arr[0]

        self.is_valid = self.valid_command_check(msg)

        if self.is_valid:

            channel_id = self.get_channel_id(self.action, cmd_text_arr)
            poke_name = self.get_poke_name_from_command(self.action, cmd_text_arr)

            # get the associated users with the command
            self.users = self.get_users(self.action, poke_name, channel_id)

    def set_live_chat_id(self, live_chat_id: str) -> None:
        """Sets the set_live_chat_id to the cmd object """

        self.live_chat_id = live_chat_id

    def set_user_name(self, channel_id: str, youtube) -> None:
        """Sets the user_name according the the action statement. """

        if self.action == "!assign":

            request = youtube.channels().list(
                part="snippet",
                id=f"{channel_id}")
            response = request.execute()

            # set user_name from the reponse
            self.user_name = response["items"][0]["snippet"]["title"]

        # otherwise check it's release
        elif self.action == "!release":

            conn = sqlite3.connect(db_pth)
            cursor = conn.cursor()
            cursor.execute("SELECT user_name \
                           FROM users WHERE \
                           poke_name = ? \
                           AND in_this_run='true'",
                           (self.poke_name.capitalize()))

            self.user_name = cursor.fetchone()[0]

        # otherwise assume it's newrun/victory
        else:
            self.user_name = ""

    def set_youtube(self, youtube) -> None:
        """ Sets the youtube object to the cmd"""
        self.youtube = youtube

    def show_data(self, cursor: sqlite3.Cursor) -> None:
        """Shows all rows in the database """

        cursor.execute("SELECT rowid, * FROM users")
        items = cursor.fetchall()

        for item in items:
            print(item)

    def convert_to_array(self, msg_text: str) -> list[str]:
        """ Executes command, mainly sql commands for the database"""

        # Strip the msg_text of white space
        msg_text = msg_text.strip()

        # split the text into an array
        msg_text = msg_text.split()

        return msg_text

    def useable_pokemon(self, user_poke_name,
                        cursor: sqlite3.Cursor) -> bool:
        """Checks if the pokemon has already been used in this run"""

        # get all the pokemon that are currently in the run
        cursor.execute("SELECT poke_name \
                       FROM users \
                       WHERE in_this_run='true'")

        poke_names = cursor.fetchall()

        for poke_name in poke_names:

            print(user_poke_name + ": " + poke_name[0])

            # check if the poke_name is in the table
            if poke_name[0] == user_poke_name:

                return False

        return True


    def useable_channel(self, user_channel_id,
                        cursor: sqlite3.Cursor) -> bool:
        """Checks if the channel has already been used in this run"""

        cursor.execute("SELECT channel_id FROM users")

        channel_ids = cursor.fetchall()

        for channel_id in channel_ids:

            print(user_channel_id + ": " + channel_id[0])

            # check if the channel is in the table
            if channel_id[0].lower() == user_channel_id.lower():

                # return false
                return False

        return True

    def valid_command_check(self, msg: Message) -> bool:
        """Checks the command is a valid command"""

        temp_text = msg.text

        user_cmd_len = len(temp_text)

        if temp_text[0] == "!":

            # strip the first ! away
            temp_text = temp_text.replace('!', '', 1)

            # split the text
            temp_text_arr = temp_text.split(' ')
            user_cmd_len = len(temp_text_arr)

            for cmd in VALID_CMDS:

                # check if the text is the current command
                if temp_text_arr[0] == cmd.cmd_str:

                    # check that the user cmd has the correct
                    # amount of params
                    if cmd.params_req == user_cmd_len:

                        return True
                    
        return False

    def victory(self, users, cursor: sqlite3.Cursor) -> None:
        """Unbans all users in chat and in the database """

        for user in users:

            # send an unban request
            request = self.youtube.liveChatBans().delete(
                id=f"{user.ban_id}"
            )

            request.execute()

            cursor.execute("UPDATE users \
                           Set banned='false' \
                           WHERE ban_id = ?",
                           (user.ban_id,))

        self.send_suc()

    class NuzlockeUser:
        """ The nuzlocke user that is asscoited with the current command

            Args:
                self - NuzlockeUser class
                user_name - display name associted with the user
                poke_name - the pokemon that is asscoiteed with the user
                channel_id - channel id that is asscoited with the user
        """
        def __init__(self, user_name: str = "", poke_name: str = "",
                     channel_id: str = "", ban_id: str = ""):
            self.user_name = user_name
            self.poke_name = poke_name
            self.channel_id = channel_id
            self.ban_id = ban_id

        def find_by_poke_name(self, poke_name):
            """ Finds the user in the table by asscoiated pokemon/sets info"""

            conn = sqlite3.connect(db_pth)
            cursor = conn.cursor()

            # search the database for the pokemon's name that are still
            # in the run
            cursor.execute("SELECT user_name, poke_name \
                           FROM users \
                           WHERE poke_name = ? \
                           AND in_this_run='true'",
                           (poke_name.capitalize()))

            # fill in the user_name and poke_name from the search
            self.user_name = cursor.fetchone()[0]
            self.poke_name = cursor.fetchone()[1]
