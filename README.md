# Nuzlocke-Bot

A python script that starts a chatbot for a specific youtube channel. It will wait for a stream for that youtube channel to go live and join once it finds one. It will then wait for commands from mods/owner of the stream and execute on those commands.


<!-- TABLE OF CONTENTS -->
<details>
  <summary>🏁 Table of Contents</summary>
  <ol>
    <li><a href="#set-up">Set Up</a></li>
    <ul>
      <li><a href="#1-using-venv">Using Venv</a></li>
      <li><a href="#2-installing-requirements">Installing Requirements</a></li>
      <li><a href="#3-setting-up-youtube-api">Setting up Youtube-API</a></li>
    </ul>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#1-running-the-program">Running the Program</a></li>
        <li><a href="#2-commands-via-youtube-chat">Commands via Youtube chat</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#help">Help</a></li>
  </ol>
</details>

# Set Up 

## 1. Using Venv

I recommend starting a virtual environment any time running this program. This helps keeps all the dependencies in one place and assures the program isn't using newer/older versions of dependencies found in requirements.txt

To start using the virtual environment paste the following in your terminal:
```zsh
pip3 install virtualenv
python3 -m venv nuzlocke-venv
source nuzlocke-venv/bin/activate
```
**_Note_**: this virtual environment needs to be activate anytime you run the script. Simply rerun the last line to activate the virtual environment.

## 2. Installing Requirements

Now that the virtual environment is set up we can install the dependencies from requirements.txt into nuzlocke-venv. 
**_Note_** this virtual environment needs to be activated anytime you run the script.
```zsh
pip3 install -r requirements.txt
```

## 3. Setting up Youtube-API
In order to make this process as easy as possible I'm going to link two youtube videos by Corey Schafer on how to enable and access the Youtube API using client secrets.

To use the Youtube API you'll need three majors things which are to 
1. Enable Youtube's API via googles developer console - https://youtu.be/th5_9woFJmk?t=35 (0:38 - 2:43)
2. Create client_secrets.json for a specific google user to use Youtube's API - https://youtu.be/vQQEaSnQ_bs?t=330 (5:30 - 10:10 )
    - What you enter for "Application name" is what will pop up when a user is asked to login in. It doesn't really matter what you call this
    - it is import for the generated client secrets file to be named "client_secrets.json"
    - "client_secrets.json" should be placed in the main directory
 3. Grant yourself access to the program. Navigate back over to http://console.cloud.google.com and click on the "OAuth consent screen tab". There will be a button called "ADD USERS", make sure to add your email and double click save. You should see your email added to the "User Information" Table.

# Usage

## 1. Starting the program

Now the program is ready to run.

In order to start up the program run the nuzlocke.py script with a youtube channel's id. If you're not sure how to find a channel's id follow this link https://support.google.com/youtube/answer/3250431?hl=en. It's also possible to find other channels id's by using Youtube's API or by using third party sites. 

```zsh
python3 nuzlocke.py <CHANNEL_ID>
```
 
The first time the program is ran it will ask for access to a google account an order to carry out commands. Google will warn the app isn't verified, click continue.

_**NOTE:**_ The account you choose will be the account replying to commands in chat. It would be worth it to set up a new google account if you want a fully dedicated bot so your personal account isn't replying to users in youtube chat.

## 1. Commands via youtube live chat


### 1. Assigning
```zsh
# assigns the pokemon snorlax to slimewiree
!assign snorlax UC1nqeQ8n8mX9FnlTUe-h3jA

# Structure of command: !assign <pokemon> <channel_id>
```
 <img src="https://github.com/zksx/nuzlocke/blob/main/gifs/assign.gif" width="300"/> 
 
  - - - -
  
 ### 2. Releasing

```zsh
# releases snorlax, thereby banning slimewire
!release snorlax

# Structure of command: !release <pokemon>
```
  <img src="https://github.com/zksx/nuzlocke/blob/main/gifs/release.gif" width="300"/>
  
  - - - -

 ### 3. New run
```bash
# Releases all pokemon caught in this run after the player's party is wiped.
!newrun
```
  <img src="https://github.com/zksx/nuzlocke/blob/main/gifs/newrun.gif" width="300"/>
  
  - - - -

### 4. Victory
```zsh
# Unban all users that had been banned from being released after the player wins the game.
!victory
```
  <img src="https://github.com/zksx/nuzlocke/blob/main/gifs/victory.gif" width="300"/>

# Roadmap 

As of right now the next plan is to intergrate a website that is able to read/write to the database. Only mods of the stream or the stream owner themselves should be able to access the website.

# Help

## 1. Commands defined

So what is a command defined as in this program? Is it the full message a user sends into the chat such as shown below?
```zsh 
!assign snorlax UCrPseYLGpNygVi34QpGNqpA
```

Or is it just the first section of the full message containing "!assign" section? It gets little muddy here, and it doesn't seem like there is a full concises if a command is just the first section or all the sections together. In order to help differentiate this confusion I've decided to call the first section the "action phrase" and the full sections a command. so for instance the command shown above, assigning snorlax a channel id, is a command. While just assigning is the action of the command. Here's an image to help illustrate what I mean.

The following command "!victory" only has 1 section, called the action section. 
```zsh
!victory
```
