import sqlite3
from valid_commands import VALID_CMDS
from message import Message


# TODO make function to reply to accounts when a command is succesful

class Command:

    def __init__(self, action = "", author_name: str = "", is_valid = False, 
                 youtube = None, livechat_id: str = "", 
                 users: list = []):
        
        self.action = action
        self.author_name = author_name
        self.is_valid = is_valid
        self.youtube = youtube
        self.livechat_id = livechat_id
        self.users = users

    """
    Name: assign
    Desc: inserts user with asscoiated poke name in database. 
    Params: 
            self - a command class object
            cursor - cursor for database
            user - the user to have the cmd exectued on
    Returns: N/A
    """
    def assign(self, user,  cursor: sqlite3.Cursor) -> None:

        # variables
        unique_channel = self.useable_channel(user.channel_id, cursor)

        unique_pokemon = self.useable_pokemon(user.poke_name, cursor)

        real_pokemon = self.real_pokemon(user.poke_name)

        # if the name is unique
        if unique_channel and unique_pokemon and real_pokemon:

            # insert the name and nickname into the database
            cursor.execute(f"INSERT INTO users VALUES ('{user.user_name}', \
                    '{user.poke_name}', 'false', 'true', '{self.author_name}', \
                    '{user.channel_id}', '' )")
            
            success_str = f'{user.user_name} has been assigned \
            to the pokemon {user.poke_name}'
            
            # send success reply
            self.send_suc(success_str)
            
        # otherwise check if the name is not unique
        elif not unique_channel:

            error_str = f'The channel "{user.channel_id}" has already been used'

            # call error
            self.send_err(error_str);
        
        elif not unique_pokemon:

            error_str = f'The pokemon "{user.poke_name}" has already been used in this run'

            # call error
            self.send_err(error_str);

            
        # otherwise the giveen pokemon name was not an actual pokemon
        else:

            error_str = f"something went wrong"

            self.send_err(error_str)

    """
    Name: assign
    Desc: inserts user with asscoiated poke name in database. 
    Params: 
            self - a command class object
            cursor - cursor for database
    Returns: N/A
    """
    def command_check(self, msg: Message) -> bool:

        temp_text = msg.text

        # check the text has a ! at the start
        if temp_text[0] == "!":

            # strip the first ! away
            temp_text = temp_text.replace('!', '', 1)

            # split the text 
            temp_text_arr = temp_text.split(" ")

            # for commands in valid commands
            for cmd in VALID_CMDS:

                # check if the text is the current command
                if temp_text_arr[0] == cmd.cmd_str:

                    # return true
                    return True
    
        # the text isn't a command
        return False

    """
    Name: execute
    Desc: Executes command, mainly sql commands for the database
    Params: 
            cmd - a command class object
    Returns: N/A
    """
    def execute(cmd) -> None:

        # creates a database first time it is ran
        conn = sqlite3.connect('databases/nuzlocke.db')

        # create a cursor
        cursor = conn.cursor()

        # check for each command
        match cmd.action:
            case "!assign":
                cmd.assign(cmd.users[0], cursor)
            
            case "!release":
                cmd.release(cmd.users[0], cursor)

            case "!newrun":
                cmd.new_run(cmd.users, cursor)

            case "!victory":
                cmd.victory(cmd.users, cursor)

            case _:
                print("command not found")

        # commit the commands
        conn.commit()
        
        # print he data base
        cmd.show_data(cursor)

    """
    Name: get_channel_id
    Desc: checks if the command is has a action that has a channel_id related 
          to it. If it does it returns the channel id.
    Params: 
            self - a command class object
            action - the command that will be executed
            cmd_text_arr - The cmd the authored entered via the youtube chat
                           but in array form.

    Returns: channel_id, or nothing
    """
    def get_channel_id(self, action: str, cmd_text_arr: list[str]):
        # get length of the command array
        cmd_len = len(cmd_text_arr)

        # check if the command is assign
        if action == "!assign":

            # return the last string from the array which is the channel id
            return cmd_text_arr[cmd_len - 1]
        
        # otherwise the command doesn't have an associted channel_id so return
        # empty string

        return ""
    

    """
    Name: get_poke_name
    Desc: gets the poke_name from the command the user entered via youtube
          if there is a poke_name
    Params: 
            self - a command class object
            action - the command that will be executed
            cmd_text_arr - The cmd the authored entered via the youtube chat
                           but in array form.
    Returns: poke_name from cmd or empty string
    """
    def get_poke_name(self, action: str, cmd_text_arr: list[str]):

        # get length of cmd_text_arr
        cmd_len = len(cmd_text_arr)
        index = 0
        poke_name = ""

        # check if the action is "!assign"
        if action == "!assign":

            # the poke_name is between the first and the last indexs

            # start index at 1 to skip the action text
            index = 1

            # loop through array and stop before the last index
            while index < cmd_len - 1:

                # add the indexed str to poke_name
                poke_name += cmd_text_arr[index]

                # add a space in between words unless it's the last word in the
                # pokemons name
                if index < cmd_len - 2:

                    # add a space
                    poke_name += " "

                # increase index
                index += 1

        # otherwise check if the action is "!release"
        if action == "!release":

            # the poke_name is the last index
            poke_name = cmd_text_arr[cmd_len - 1]

            # return the last index of the array
            return poke_name
        
        # other wise there is no pokename so return empty strings
        return poke_name
        

    """
    Name: get_users
    Desc: gets the users associated with the command. This could be one user
          in the case of release/assign or many users such as with victory and
          newrun.
    Params: 
            self - a command class object
            action - the command that will be executed
            poke_name - pokemon name associated with the user
            channel_id - channel id of associated user
    Returns: an array of user(s)
    """
    def get_users(self, action: str, poke_name:str, channel_id: str):
            
        # creates a database first time it is ran
        conn = sqlite3.connect('databases/nuzlocke.db')

        # create a cursor
        cursor = conn.cursor()

        # check if the action is assign
        if action == "!assign":

            # the user doesn't exist yet

            # make a request for the users display name
            request = self.youtube.channels().list(
                part="snippet",
                id=f"{channel_id}"
            )
            response = request.execute()

            user_name = response["items"][0]["snippet"]["title"]

            # make a new user / fill in user details
                # poke_name
                # channel_id
            user = [self.NuzlockeUser(user_name, poke_name, channel_id)]

            # return user
            return user

        # otherwise check if the action is !release
        elif action == "!release":
            # the user exists

            # search the database by poke_name, returning the channel_id,
            # poke_name, and user_name
            cursor.execute(f"SELECT channel_id, poke_name, user_name \
                           FROM users \
                           WHERE poke_name = ? AND \
                           in_this_run='true'", (poke_name))

            user_data = cursor.fetchone()
            
            channel_id = user_data[0]
            poke_name = user_data[1]
            user_name = user_data[2]

            # make a new user / set 
            # channel_id
            # poke_name 
            # user_name
            user = [self.NuzlockeUser(user_name, poke_name, channel_id, "")]

            # return user
            return user

        # otherwise check the action is !newrun
        elif action == "!newrun":
            # the user(s) exists

            # search the database by in the in_the_run, returning channel_ids,
            # and user_names, poke_name
            cursor.execute(f"SELECT channel_id, poke_name, user_name  \
                FROM users \
                WHERE in_this_run='true' AND banned='false'")
            
            users = cursor.fetchall()

            users_arr = []

            index = 0
            # for user in users
            for user in users:

                channel_id = users[index][0]
                poke_name = users[index][1]
                user_name = users[index][2]

                # make a new user / set 
                # user_name
                # poke_name
                # channel_id
                user = self.NuzlockeUser(user_name, poke_name, channel_id, "")

                # append to user_arr
                users_arr.append(user)

                # increase index
                index += 1

            # return list of users
            return users_arr

        # otherwise the action is !victory
        else:
            # the user(s) exists

            # search the database returning all banned users with their 
            # user_name, and ban_id
            cursor.execute(f"SELECT user_name, ban_id  \
            FROM users \
            WHERE banned='true'")

            users = cursor.fetchall()

            users_arr = []

            index = 0

            # for user in users
            for user in users:
                user_name = users[index][0]
                ban_id = users[index][1]

                # make a new user
                # set the user(s) ban_id and user_name
                user = self.NuzlockeUser(user_name, "", "", ban_id)

                users_arr.append(user)

                # increase index
                index += 1

            return users_arr
        

    """
    Name: new_run
    Desc: sets all pokemon in the run to the banned status. Also bans all the 
          users in youtube chat.
    Params: 
            self - a command class object
    Returns: N/A
    """
    def new_run(self, users, cursor: sqlite3.Cursor) -> None:

        # for user in users
        for user in users:

            # ban this user
            self.release(user, cursor)

        # release all the pokemon 
            # method: release all

        num_of_users = len(users)

        # Update the database and seet the users in this run to be banned and not in the 
        # run anymore.
        cursor.execute("UPDATE users SET banned='true', in_this_run='false' WHERE in_this_run='true'")

        success_str = f"{num_of_users} helpless victims have been banned"

        self.send_suc(success_str)


    """
    Name: real_pokmon
    Desc: checks to make sure the pokemon entered in the command is a real 
          pokemon via the pokemon database
    Params: 
            self - a command class object
    Returns: N/A
    """
    def real_pokemon(self, user_poke_name) -> bool:
        # connect to pokemon database
        conn = sqlite3.connect('databases/pokemon.db') 
        cursor = conn.cursor()

        # get all the pokemon names
        cursor.execute("SELECT name FROM pokemon;")
        poke_names = cursor.fetchall()

        # make the poke name lower cased and no whitespace
        tmp_poke_name = user_poke_name.lower()
        tmp_poke_name = user_poke_name.replace("", "")

        for poke_name in poke_names:

            # save the og pokemon name with spaces/caps
            orignial_name = poke_name[0]

            # assign the one str in the arr poke_name to poke_name for ease
            poke_name = poke_name[0]

            # strip pokemon name of white space
            poke_name = poke_name.replace(" ", "")

            # lower case it
            poke_name = poke_name.lower()

            print(tmp_poke_name + ": " + poke_name)

            # check if the poke_name is in the database
            if tmp_poke_name == poke_name:

                # set the cmds pokee_name to the pokemon name with white space
                # and caps
                user_poke_name = orignial_name

                # return true
                return True
        
        # return false
        return False

    """
    Name: release
    Desc: To be used when a pokemon is released in the wild. This bans the 
          users assigned to that pokemon
    Params: 
            self - a command class object
            cursor - belongs to the nuzlocke database
    Returns: N/A
    """
    def release(self, user, cursor: sqlite3.Cursor) -> None:


                # execute datebase update
        cursor.execute(f"UPDATE users SET banned='true' WHERE poke_name = ? AND \
                       channel_id = ?", (user.poke_name, user.channel_id ))


        request = self.youtube.liveChatBans().insert(
            part="snippet",
            body={
            "snippet": {
                "liveChatId": f"{self.livechat_id}",
                "type": "permanent",
                "bannedUserDetails": {
                "channelId": f"{user.channel_id}"
                }
            }
            }
        )
        response = request.execute()

        ban_id = response["id"]

        cursor.execute(f"UPDATE users SET ban_id = ? WHERE \
                       channel_id = ?", (ban_id,user.channel_id ))

        success_str = f'The user "{user.user_name}" has been banned'
            
        # send success reply
        self.send_suc( success_str)

    """
    Name: send_err
    Desc: sends an error message via chat to the author of the command
    Params: 
            self - a command class object
            err_str - a preset error message
    Returns: N/A
    """
    def send_err(self, err_str: str) -> None:

        request = self.youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                "liveChatId": f"{self.livechat_id}",
                "type": "textMessageEvent",
                "textMessageDetails": {
                    "messageText": f"@{self.author_name} Error: {err_str}"
                }
                }
            })

        # send message
        request.execute()

    """
    Name: send_suc
    Desc: sends an success message via chat to the author of the command
    Params: 
            self - a command class object
            err_str - a preset success message
    Returns: N/A
    """
    def send_suc(self, suc_str: str) -> None:

        # QUOTA COST 50    
        request = self.youtube.liveChatMessages().insert(
        part="snippet",
        body={
            "snippet": {
            "liveChatId": f"{self.livechat_id}",
            "type": "textMessageEvent",
            "textMessageDetails": {
                "messageText": f"@{self.author_name} {suc_str}"
            }
            }
        })

        # send message
        request.execute()

    """
    Name: set_cmd
    Desc: sets all the cmd attributes from the msg
    Params: 
            msg_text_arr - string array of text
    Returns: N/A
    """

    #TODO make it so assign and release both work easily
    def set_cmd(self, msg_text_arr: list[str]) -> None:

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

            # assign all the indexs between the first and last to the poke_name
            while i < poke_name_length:

                # assign indexed text to poke_name
                self.poke_name += msg_text_arr[i]

                # add a space inbetween while if the pokemons name and not at the
                # end of their name: i.e: "Roaring Moon", not "Roaring Moon "
                if i < text_arr_len - 2:

                    # add space
                    self.poke_name += " "

                # increase the index
                i+=1

            if text_arr_len > 2:
                # assign the channel id to the command channel_id
                self.channel_id = msg_text_arr[text_arr_len - 1]

    """
    Name: set_full
    Desc: sets all the cmd attributes from the msg
    Params: 
            msg - Message class
    Returns: An array with the msg split into strings
    """
    def set_full(self, msg: Message, youtube, livechat_id: str) -> None:

        # set the authors name
        self.author_name = msg.author_name

        # split the text into an array
        cmd_text_arr = self.standarize_msg(msg.text)

        # set the action to be executed
        self.action = cmd_text_arr[0]

        # attempt to get channel_id
        channel_id = self.get_channel_id(self.action, cmd_text_arr)

        # attempt to get poke_name
        poke_name = self.get_poke_name(self.action, cmd_text_arr)

        # set the youtube object
        self.set_youtube(youtube)

        # set live chat id
        self.set_livechat_id(livechat_id)

        # get the associated users with the command
        self.users = self.get_users(self.action , poke_name, channel_id)


    def set_livechat_id(self, livechat_id: str) -> None:
        self.livechat_id = livechat_id

    def set_user_name(self, channel_id: str, youtube) -> None:

        if self.action == "!assign":

            # use channel id to find display name
            request = youtube.channels().list(
            part="snippet",
            id=f"{channel_id}"
            )

            # sending request and getting response
            response = request.execute()


            self.user_name = response["items"][0]["snippet"]["title"]

        # otherwise check it's release
        elif self.action == "!release":

            # creates a database first time it is ran
            conn = sqlite3.connect('databases/nuzlocke.db')

            # create a cursor
            cursor = conn.cursor()

            # get user_name from database using the pokemons name
            cursor.execute(f"SELECT user_name FROM users WHERE \
                           poke_name = ? \
                           AND in_this_run='true'", (self.poke_name.capitalize()))

            self.user_name = cursor.fetchone()[0]

        #otherwise assume it's newrun
        else:
            self.user_name = ""

    def set_youtube(self, youtube) -> None:
        self.youtube = youtube

    """
    Name: show_data
    Desc: shows all rows in the database
    Params: 
            self - a command class object
            cursor - cursor for database
    Returns: N/A
    """
    def show_data(self, cursor: sqlite3.Cursor) -> None:

        cursor.execute("SELECT rowid, * FROM users")

        items = cursor.fetchall()

        for item in items:
            print(item)

    """
    Name: standarize_msg
    Desc: executes command, mainly sql commands for the database
    Params: 
             msg_text - text from the msg class
    Returns: An array with the msg split into strings
    """
    def standarize_msg(self, msg_text: str) -> list[str]:

        # Strip the msg_text of white space
        msg_text = msg_text.strip()

        # split the text into an array
        msg_text = msg_text.split()

        return msg_text

    """
    Name: useable_pokemon
    Desc: checks if the pokemon has already been used in this run
    Params: 
             self - Command class
             cursor - for the nuzlocke database
    Returns: An array with the msg split into strings
    """
    def useable_pokemon(self, user_poke_name, cursor: sqlite3.Cursor) -> bool:

        # get all the pokemon that are currently in the run
        cursor.execute("SELECT poke_name FROM users WHERE in_this_run='true'")
        poke_names = cursor.fetchall()

        # for every poke_name in the database
        for poke_name in poke_names:

            print(user_poke_name + ": " + poke_name[0])

            # check if the poke_name is in the database
            if poke_name[0] == user_poke_name:

                # return false
                return False
        
        # return true
        return True

    """
    Name: useable_channel
    Desc: checks if the pokemon has already been used in this run
    Params: 
             self - Command class
             cursor - for the nuzlocke database
    Returns: An array with the msg split into strings
    """
    def useable_channel(self, user_channel_id, cursor: sqlite3.Cursor) -> bool:

        # gather user names in database
        cursor.execute("SELECT channel_id FROM users")

        channel_ids = cursor.fetchall()

        # for every user name in the database
        for channel_id in channel_ids:
            print(user_channel_id + ": " + channel_id[0])

            # check if the username is in the database
            if channel_id[0].lower() == user_channel_id.lower():

                # return false
                return False

        return True
    
    """
    Name: victory
    Desc: unbans all users in chat and in the database
    Params: 
             self - Command class
             cursor - for the nuzlocke database
    Returns: N/A
    """
    def victory(self, users, cursor: sqlite3.Cursor) -> None:
        
        # for user in users
        for user in users:

            # send an unban request
            request = self.youtube.liveChatBans().delete(
                id=f"{user.ban_id}"
            )
            request.execute()

            # update sql 
            cursor.execute(f"UPDATE users Set banned='false' \
                           WHERE ban_id = ?", (user.ban_id))

            suc_str = f"{user.user_name} is unbanned!"

            self.send_suc(suc_str)


    """
    Name: NuzlockeUser
    Desc: The nuzlocke user that is asscoited with the current command
    Attrs: 
             self - NuzlockeUser class
             user_name - display name associted with the user
             poke_name - the pokemon that is asscoiteed with the user
             channel_id - channel id that is asscoited with the user
    Returns: N/A
    """
    class NuzlockeUser:
        def __init__(self, user_name: str = "", poke_name: str = "", 
                     channel_id: str = "", ban_id: str = ""):
            self.user_name = user_name
            self.poke_name = poke_name
            self.channel_id = channel_id
            self.ban_id = ban_id
        
        """
        Name: find_by_channel_id
        Desc: finds the user in the database by channel_id
        params: 

        Returns: N/A
        """
        def find_by_channel_id():
            pass

        """
        Name: find_by_poke_name
        Desc: finds the user in the database by asscoiated pokemon. Sets the
              remaining info for the user as well
        params: 
                self - NuzlockeUser class
                poke_name - the pokemon that is associated with the user
        Returns: N/A
        """
        def find_by_poke_name(self, poke_name):

            # make a connection to the nuzlocke database
                        # creates a database first time it is ran
            conn = sqlite3.connect('databases/nuzlocke.db')

            # make a cursor to the database
            cursor = conn.cursor()

            # search the database for the pokemon's name that are still
            # in the run
            cursor.execute(f"SELECT user_name, poke_name FROM users \
                           WHERE poke_name = ? \
                           AND in_this_run='true'", (poke_name.capitalize())

            # fill in the user_name and poke_name from the search
            self.user_name = cursor.fetchone()[0]
            self.poke_name = cursor.fetchone()[1]
