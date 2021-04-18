# PoETiS
Path of Exile Tiers in Stash tool allows you to scan your stash for items with specified modifier values.

Works in Ultimatum league, just change league name to "Ultimatum" in settings.

## Limitations

One stash at a time, doesn't have to be premium, just normal or quad stash with items. You can switch between stashes if you added more than one in settings.

Only identified rare and magic items, you can have other items in stash, but they won't be processed.

Pseudo mods are not supported, I may add them in future.

Depending on GGG servers load you may need to wait a bit after putting items into the stash.

GGG API limits items returned to 100 of the same type, so if you dump over 100 rings in your stash, some of them won't be processed and you won't know about it.

## Setup
You can download a prepared executable or run from sources (just install all dependencies from requirements.txt).
After you run it for the first time, a new file "config.xml" will be created in the location of the executable and you will see a widget bar on the left edge of your screen.

1. Check buttons description below if something is not clear.
2. Go to settings, set account name, session ID, add at least one stash name and adjust net position and size to fit your inventory
3. Click "run" button, if you want to show/hide frames click pencil
4. Switch between stashes with <> buttons, each time you will need to send new request. Tooltip with name of stash will disappear once you hit "run" button or hide all buttons.
5. You may want to modify filters, described below. For example jewels have too many mods, I added one mod per jewel category, but you probably will want much more.

![](https://i.ibb.co/wZnkPZ0/widget-multi.png)
![](https://i.ibb.co/tZw1kBF/widget-hidden1.png)

Buttons:
1. Allows to drag widget by the left edge, when clicked hides and shows rest of the buttons.
2. Switch between multiple stash tabs. Current stash name is displayed after switch, text disappears once you hit "run" button or hide all buttons.
3. Sends request for items data, maximum once per second (processing takes longer than that). You need to have valid data in settings, described below.
4. After button 2. icon gets back from "hourglass" to "play", you can toggle on/off frames.
5. Mods list. Initial list is an example, if you don't like it, turn off the tool (last button) and replace content of filters/mods.xml with filters/mods_empty.xml or delete all mods one by one from mods list window.
You can delete mods by removing cell content and add new ones modifying default mod message at the end of each section. Each mod needs to have at least one numeric value and HAS to be lowercase, it won't be detected if it is has any upper case.
6. Settings. With first run you will need to provide data to all fields, add stashes and adjust net accordingly.
Slider determines how many mods in item should have value greater or equal to your filter to be detected and have color frame.
You can modify colors in settings.xml after you exit tool, just make sure it meets QColor constructor [requirements](https://doc.qt.io/qt-5/qcolor.html).
Guide how to get session ID - [here](https://github.com/Stickymaddness/Procurement/wiki/SessionID). Remember it will change over time, so if you get error message about invalid session ID or no connection, you may need to provide new session ID.
7. Terminates tool. All settings data is saved at the moment you edit it.

Example of frames. Each color represents number of mods that meet requirements specified in your filter. Brown - one good mod, blue - two mods etc. Dashed frame means that item doesn't have open affixes:

![](https://i.ibb.co/1XTGN45/borders-dash.png)


![](https://i.ibb.co/0qhjLHh/colors.png)

### Linux

1. Install the dependencies: `pip install -r requirements.linux.txt`
2. Run the main script: `/path/to/MainWidget.py` or `python MainWidget.py`

## Windows defender / antivirus
To create one executable file I'm using pyinstaller. Because of that your antivirus software may find it suspicious, see official pyinstaller [response](https://github.com/pyinstaller/pyinstaller/issues/4633). If you want to run the tool from sources just install python 3.8.2 and all packages from requirements.txt. If you have any troubles with that, let me know on [reddit](https://www.reddit.com/r/pathofexile/comments/h86xw2/poe_tiers_in_stash_tool/).

## Attributions
Buttons used in project were made by:
 [Freepik](https://www.flaticon.com/authors/freepik)
 [Google](https://www.flaticon.com/authors/google)
 [Becris](https://www.flaticon.com/authors/becris)
 [Pixel perfect](https://www.flaticon.com/authors/pixel-perfect)
 [Smashicons](https://www.flaticon.com/authors/smashicons)
from www.flaticon.com
