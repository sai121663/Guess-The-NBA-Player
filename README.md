### For non-programmers...

Download Game.exe and start playing!

### How to update player data? 

Go to Backend.py -> change **update_casual_players()** and/or **update_diehard_players()**

> The new dictionary file(s) will be stored under Datasets -> casual_players.json or diehard_players.json


### How to rebuild .exe file? 

Run 'pyinstaller Frontend.spec' in the terminal 

> Only works if the three main folders ('Audio', 'Images', 'Datasets') aren't changed 
