# YayaBot-Rewrite
 
Rewrite for YayaBot since I don't really like working with the old code lmao

# Running

For any commands:
- change py to python3 if you're not on windows
- run in base YayaBot-Rewrite dir unless specifically told to
- don't sudo lmao

I'd recommend making a venv and then activating it:

`py -m venv .venv`

`.venv\Scripts\activate` on Windows else `.venv/bin/activate`

Then installing requirements.txt

`py -m pip install -r requirements.txt`

put your bot token in TOKEN.txt

and run simply with

`py bot.py`

# Vscode Setup

Files edited here will be in `.vscode`

Edit your `launch.json` to the program be `${workspaceFolder}\\bot.py`
This will make you easily able to launch bot.py while editing a cog or something else

Edit your `settings.json` to have `"python.autoComplete.extraPaths": ["${workspaceFolder}/"]` in it, make sure it's correctly json formatted and stuff.
This will add autocomplete for the yaya module