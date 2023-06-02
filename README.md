# nuzlocke

A python script that starts a chatbot for a specific youtube channell. It will wait for a stream for that youtube channel to go live and join once it finds one. It will then wait for commands from mods/owner of the stream and execute on those commands.

## Set up 

### Using Venv

I recommend starting a virtual environment. This helps keeps all the dependencies in one place and assures the program isn't using newer/older versions of dependencies found in requirements.txt

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
_Note this virtual enviroment needs to be activate anytime you run the script._

### Installing Requirements

Now that the virtual enviroment is set up we can install the dependencies from requirements.txt into nuzlocke-venv. Note this virtual eniroment needs to be activate anytime you run the script.
```bash
pip3 install -r requirements.txt
```

### Setting up Youtube-API
To use the Youtube API you'll need two majors things which are
1. Enable Youtube's API via googles developer console - https://youtu.be/th5_9woFJmk?t=35 watch (0:38 - 2:43)
2. Create client_secrets.json for a specfic google user to use Youtube's API - https://youtu.be/vQQEaSnQ_bs?t=330 watch (5:30 - 10:10 )
    - What you enter for "Application name" is what will pop up when a user is asked to login in. It doesn't really matter what you call this
    - it is import for the generated client secrets file to be named "client_secrets.json"
    - "client_secrets.json" should be placed in the main directory

An order to save time and avoid posting a wall of text here I'm going to referenece two youtube videos by Corey Schafer on how to enable and access the Youtube API using 0auth2.

