# nuzlocke

A python script that starts a chatbot for a specific youtube channell. It will wait for a stream for that youtube channel to go live and join once it finds one. It will then wait for commands from mods/owner of the stream and execute on those commands.

## Set up 

### Using Venv

I recommend starting a virtual environment. This helps keeps all the dependencies in one place and assures the program isn't using newer/older versions of dependencies found in requirements.txt
```bash
pip3 install virtualenv
```

Then to start the virtual enviroment with the name 'nuzlocke-venv' use the following command:
```bash
python3 -m venv nuzlocke-venv
```

To activate the virtual enviroment use the following command:
```bash
source nuzlocke-env/bin/activate
```

### Installing Requirements

Know that the virtual enviroment is set up we can install the dependencies from requirements.txt into the nuzlocke-venv.
```bash
pip3 install -r requirements.txt
```
