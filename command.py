import sqlite3
from valid_commands import VALID_CMDS
from message import Message


# TODO make function to reply to accounts when a command is succesful

class Command:

    def __init__(self, cmd = "", user_name: str = "", poke_name: str = "", 
                 author_name: str = "", is_valid = False, youtube = None, 
                 livechat_id: str = ""):
        
        self.cmd = cmd
        self.user_name = user_name
        self.poke_name = poke_name
        self.author_name = author_name
        self.is_valid = is_valid
        self.youtube = youtube
        self.livechat_id = livechat_id

    """
    Name: assign
    Desc: inserts user with asscoiated poke name in database. 
    Params: 
            self - a command class object
            cursor - cursor for database
    Returns: N/A
    """
    def assign(self, cursor: sqlite3.Cursor) -> None:

        # variables
        unique_name = self.useable_user_name(cursor)

        unique_pokemon = self.useable_pokemon(cursor)

        real_pokemon = self.real_pokemon()

        # if the name is unique
        if unique_name and unique_pokemon and real_pokemon:

            # insert the name and nickname into the database
            cursor.execute(f"INSERT INTO users VALUES ('{self.user_name}', '{self.poke_name}', 'false', 'true')")
            
            success_str = f'The user name "{self.user_name}" has been assigned to the pokemon "{self.poke_name}"'
            
            # send success reply
            self.send_suc(success_str)
            
        # otherwise check if the name is not unique
        elif not unique_name:

            error_str = f'The user name "{self.user_name}" has already been used'

            # call error
            self.send_err(error_str);
        
        elif not unique_pokemon:

            error_str = f'The pokemon "{self.poke_name}" has already been used in this run'

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
                cmd.assign(cursor)
            
            case "!release":
                cmd.release(cursor)

            case "!newrun":
                cmd.new_run(cursor)

            case "!victory":
                cmd.victory(cursor)

            case _:
                print("command not found")

        # commit the commands
        conn.commit()
        
        # print he data base
        cmd.show_data(cursor)

    """
    Name: new_run
    Desc: sets all pokemon in the run to the banned status. Also bans all the 
          users in youtube chat
    Params: 
            self - a command class object
    Returns: N/A
    """
    def new_run(self, cursor: sqlite3.Cursor) -> None:

        # gather all users where in_this_run is true
        cursor.execute("SELECT user_name FROM users WHERE in_this_run='true'")
        user_names = cursor.fetchall()

        # TODO implement below 
        # for user in users

            # ban this user

        # release all the pokemon 
            # method: release all

        num_of_users = len(user_names)

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
    def real_pokemon(self) -> bool:
        # connect to pokemon database
        conn = sqlite3.connect('databases/pokemon.db') 
        cursor = conn.cursor()

        # get all the pokemon names
        cursor.execute("SELECT name FROM pokemon;")
        poke_names = cursor.fetchall()

        # make the poke name lower cased and no whitespace
        tmp_poke_name = self.poke_name.lower()
        tmp_poke_name = self.poke_name.replace("", "")

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
                self.poke_name = orignial_name

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
    def release(self, cursor: sqlite3.Cursor) -> None:

        # TODO check that the user is in the nuzlocke user base

        # execute datebase update
        cursor.execute(f"UPDATE users SET banned='true' WHERE poke_name='{self.poke_name}'")
        
        # get user_name from database using the pokemons name
        cursor.execute(f"SELECT user_name FROM users WHERE poke_name='{self.poke_name}'")

        self.user_name = cursor.fetchone()[0]

        # TODO execute youtube chat ban

        success_str = f'The user "{self.user_name}" has been banned'
            
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
    def set_cmd(self, msg_text_arr: list[str]) -> None:

        text_arr_len = len(msg_text_arr)

        self.cmd = msg_text_arr[0]

        if text_arr_len > 1:

            # index at 1 to skip the action command beiong assigned
            i = 1

            # assign all the indexs between the first and last to the poke_name
            while i < text_arr_len - 1:

                # assign indexed text to poke_name
                self.poke_name += msg_text_arr[i]

                # add a space inbetween while if the pokemons name and not at the
                # end of their name: i.e: "Roaring Moon", not "Roaring Moon "
                if i < text_arr_len - 2:

                    # add space
                    self.poke_name += " "

                # increase the index
                i+=1

            # assign the user name to the user_name
            self.user_name = msg_text_arr[text_arr_len - 1]

    """
    Name: set_full
    Desc: sets all the cmd attributes from the msg
    Params: 
            msg - Message class
    Returns: An array with the msg split into strings
    """
    def set_full(self, msg: Message, youtube, livechat_id: str) -> None:

        self.author_name = msg.author_name

        text_arr = self.standarize_msg(msg.text)

        self.set_cmd(text_arr)

        self.set_youtube(youtube)
        
        self.set_livechat_id(livechat_id)

    def set_livechat_id(self, livechat_id: str) -> None:
        self.livechat_id = livechat_id

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
    def useable_pokemon(self, cursor: sqlite3.Cursor) -> bool:

        # get all the pokemon that are currently in the run
        cursor.execute("SELECT poke_name FROM users WHERE in_this_run='true'")
        poke_names = cursor.fetchall()

        # for every poke_name in the database
        for poke_name in poke_names:

            print(self.poke_name + ": " + poke_name[0])

            # check if the poke_name is in the database
            if poke_name[0] == self.poke_name:

                # return false
                return False
        
        # return true
        return True

    """
    Name: useable_user_name
    Desc: checks if the pokemon has already been used in this run
    Params: 
             self - Command class
             cursor - for the nuzlocke database
    Returns: An array with the msg split into strings
    """
    def useable_user_name(self, cursor: sqlite3.Cursor) -> bool:

        # gather user names in database
        cursor.execute("SELECT user_name FROM users")

        user_names = cursor.fetchall()

        # for every user name in the database
        for user_name in user_names:
            print(self.user_name + ": " + user_name[0])

            # check if the username is in the database
            if user_name[0].lower() == self.user_name.lower():

                # return false
                return False

        return True
    
    """
    Name: victory
    Desc: unbans all users in chat and in thee database
    Params: 
             self - Command class
             cursor - for the nuzlocke database
    Returns: N/A
    """
    def victory(self, cursor: sqlite3.Cursor):
        pass
