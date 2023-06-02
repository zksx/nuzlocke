# Nuzlocke-Bot

A python script that starts a chatbot for a specific youtube channell. It will wait for a stream for that youtube channel to go live and join once it finds one. It will then wait for commands from mods/owner of the stream and execute on those commands.

## Set up 

### Using Venv

I recommend starting a virtual environment any time running this program. This helps keeps all the dependencies in one place and assures the program isn't using newer/older versions of dependencies found in requirements.txt

First install virtualenv using pip3
```bash
pip3 install virtualenv
```

Then to create the virtual enviroment with the name 'nuzlocke-venv' use the following command:
```bash
python3 -m venv nuzlocke-venv
```

Now activate the virtual enviroment use the following command:
```bash
source nuzlocke-env/bin/activate
```
**_Note_**: this virtual enviroment needs to be activate anytime you run the script.

### Installing Requirements

Now that the virtual enviroment is set up we can install the dependencies from requirements.txt into nuzlocke-venv. 
**_Note_** this virtual eniroment needs to be activate anytime you run the script.
```bash
pip3 install -r requirements.txt
```

### Setting up Youtube-API
An order to make this process at easy as possible I'm going to link two youtube videos by Corey Schafer on how to enable and access the Youtube API using client secrets.

To use the Youtube API you'll need threee majors things which are
1. Enable Youtube's API via googles developer console - https://youtu.be/th5_9woFJmk?t=35 (0:38 - 2:43)
2. Create client_secrets.json for a specfic google user to use Youtube's API - https://youtu.be/vQQEaSnQ_bs?t=330 (5:30 - 10:10 )
    - What you enter for "Application name" is what will pop up when a user is asked to login in. It doesn't really matter what you call this
    - it is import for the generated client secrets file to be named "client_secrets.json"
    - "client_secrets.json" should be placed in the main directory
 3. Grant yourself access to the program. Naviagate back over to http://console.cloud.google.com and click on the "OAuth constent screen tab". There will be a button called "ADD USERS", make sure to add your email and double click save. You should see your email added to the "User Information" Table.

## Usage

### Running the program

Now the program is ready to run.

In order to start up the program run the yt.py script with a youtube channels id. If your not sure how to find a channels id follow this link https://support.google.com/youtube/answer/3250431?hl=en. It's also possible to find other channels id's by using Youtube's API.

```zsh
python3 yt.py <CHANNEL_ID>
```
 
The first time the program is ran it will ask for access to a google account an order to carry out commands. Google will warn the app isn't verified, click continue.

_**NOTE:**_ The account you choose will be the account replying to commands in chat. It would be worth it to set up a new google account if you want a fully dedicated bot so your personal account isn't replying to users in youtube chat.

### Commands via Youtube chat
```python
# assigns the pokemon snorlax to zksx
!assign snorlax zksx

# releases snorlax, thereby banning zksx
!release snorlax

# Releases all pokemon caught in this run after the players party is wiped.
!newrun

# Unban all users that had been banned from being released after the player wins the game.
!victory
```
