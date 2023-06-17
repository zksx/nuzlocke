import sqlite3

from commands.command import Command
from commands.message import Message

cmd = Command("!assign", "zksx", False, None, "fake_chat_id", 
              users=[Command.NuzlockeUser("slimewire", "snorlax", "UC1nqeQ8n8mX9FnlTUe-h3jA")] )

cmd2 = Command("!assign", "zksx", False, None, "fake_chat_id", 
              users=[Command.NuzlockeUser("slimewire", "mew", "UC1nqeQ8n8mX9FnlTUe-h3jA")] )

# user strings
us_assign = "!assign snorlax UC1nqeQ8n8mX9FnlTUe-h3jA"
us_release = "!release snorlax"
us_newrun = "!newrun"
us_victory = "!victory"

# user arrays
ua_assign = ["!assign", "snorlax", "UC1nqeQ8n8mX9FnlTUe-h3jA"]
ua_release = ["!release", "snorlax"]
ua_newrun = ["!newrun"]
ua_victory = ["!victory"]

def test_get_poke_name():

    # TEST 1 ASSIGN
    result = cmd.get_poke_name("!assign", ua_assign)
    assert result == "snorlax"

    # TEST 2 RELEASE
    user_arr = ["!release", "snorlax"]
    result = cmd.get_poke_name("!release", ua_release)
    assert result == "snorlax"

    # TEST 3 NEWRUN
    user_arr = ["!newrun", ""]
    result = cmd.get_poke_name("!newrun", ua_newrun)
    assert result == ""

    # TEST 4 Victory
    user_arr = ["!victory", ""]
    result = cmd.get_poke_name("!victory", ua_victory)
    assert result == ""

def test_get_channel_id():

    result = cmd.get_channel_id("!assign", ["!assign", "snorlax", "fake_channel_id"])
    assert result == "fake_channel_id"

    result = cmd.get_channel_id("!release", ["!release", "snorlax"])
    assert result == ""


def test_get_poke_name():
     
     result = cmd.get_poke_name("!assign", ["!assign", "snorlax", "fake_channel_id"])

     assert result == "snorlax"

def test_real_pokemon():
     
     # Testing with a real pokemon
     result = cmd.real_pokemon("snorlax")

     assert result == True

     # Testing with a fake pokemon
     result = cmd.real_pokemon("fake name")

     assert result == False

def test_standardize_msg():
    
        # TEST 1 Assign
        result = cmd.standarize_msg(us_assign)

        assert result == ua_assign

        # TEST 2 Release
        result = cmd.standarize_msg(us_release)

        assert result == ua_release

        # TEST 3  Newrun
        result = cmd.standarize_msg(us_newrun)

        assert result == ua_newrun

        # TEST Victory
        result = cmd.standarize_msg(us_victory)

        assert result == ua_victory

def test_useable_pokemon():
        conn = sqlite3.connect('databases/test_nuzlocke.db')
        cursor = conn.cursor()

        # TEST 1 Testing for the pokemon already being in the database
        user = cmd.users[0]
        result = cmd.useable_pokemon(user.poke_name, cursor)
        assert result == False

        # TEST 2 Testing for the pokemon not being in the database
        user = cmd2.users[0]
        result = cmd2.useable_pokemon(user.poke_name, cursor)
        assert result == True

def test_valid_command_check():
    msg_a = Message("zksx", us_assign, True, False)
    msg_r = Message("zksx", us_release, True, False)
    msg_nr = Message("zksx", us_newrun, True, False)
    msg_v = Message("zksx", us_victory, True, False)
    msg_bad = Message("zksx", "!asdsa snorlax dhsaifhu", True, False)
    msg_bad2 = Message("zksx", "assign snorlax dhsaifhu", True, False)

    result_a = cmd.valid_command_check(msg_a)
    result_r = cmd.valid_command_check(msg_r)
    result_nr = cmd.valid_command_check(msg_nr)
    result_v = cmd.valid_command_check(msg_v)
    result_bad = cmd.valid_command_check(msg_bad)
    result_bad2 = cmd.valid_command_check(msg_bad2)

    assert result_a == True
    assert result_r == True
    assert result_nr == True
    assert result_v == True
    assert result_bad == False
    assert result_bad2 == False

def test_get_users():
     pass
