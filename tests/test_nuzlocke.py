import pytest

from nuzlocke import *
from .mock_reponses import responses_dict
from commands.message import Message

def test_get_offline_at():
    
    with pytest.raises(KeyError):
            
            lcm_l_reponse = responses_dict["live chat message list"]
            get_offline_at(lcm_l_reponse.json())

def test_get_next_pt():

    lcm_l_reponse = responses_dict["live chat message list"]

    result = get_next_pt(lcm_l_reponse.json())

    assert result == "GJjzsISZwf8CIKPQ2byZwf8C"

def test_get_wait_time():

    lcm_l_reponse = responses_dict["live chat message list"]

    result = get_wait_time(lcm_l_reponse.json())

    assert result == 4802

"""
def test_get_live_chat_id():
     
    v_l_reponse = responses_dict["video list"]

    result = get_live_chat_id()


    assert result == "Cg0KC2pmS2ZQZnlKUmRrKicKGFVDU0o0Z2tWQzZOcnZJSTh \
                     1bXp0ZjBPdxILamZLZlBmeUpSZGs"
"""

def test_get_permissions():
     
     # TESTING IF MOD HAS PERMISSIONS
    msg1 = Message(author_name="teamchoss", 
                text="!assign snorlax slimewire", 
                is_mod=True, 
                is_owner=False)
    
    result = get_permissions(msg1)

    assert result == True

    # TESTING IF OWNER HAS PERMISSIONS
    msg2 = Message(author_name="teamchoss", 
                text="!assign snorlax slimewire", 
                is_mod=False, 
                is_owner=True)
    
    result = get_permissions(msg2)

    assert result == True

    # TESTING IF NON MOD/OWNER DOESN'T HAVE PEERMISSIONS
    msg3 = Message(author_name="teamchoss", 
                   text="!assign snorlax slimewire", 
                   is_mod=False, 
                   is_owner=False)
    
    result = get_permissions(msg3)

    assert result == False

def test_get_stream_status():
    
    # THE REPONSE PASSED DOESN'T HAVE A "offlineAt" KEY, THIS SHOULD
    # RETURN TRUE
    lcm_l_reponse = responses_dict["live chat message list"]

    result = get_stream_status(lcm_l_reponse.json())
    
    assert result == True

    lcm_l_offline_reponse = responses_dict["live chat message list offline"]

    result = get_stream_status(lcm_l_offline_reponse.json())
    
    assert result == False