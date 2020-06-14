# PoETiS
Path of Exile Tiers in Stash tool allows you to scan your stash for items with specified modifier values.

## Limitations

As of 13.06.2020 PoE Vulkan stays on top of everything, so if you want to use Vulkan and any 3rd party tool you need to run game in windowed mode (not windowed fullscreen).
Bug was already reported [here](https://www.pathofexile.com/forum/view-thread/2867255).
There is [workaround](https://www.reddit.com/r/pathofexile/comments/gseuoy/vulkan_test_technical_megathread/fs6tie9/?utm_source=reddit&utm_medium=usertext&utm_name=pathofexile&utm_content=t1_fsufmjb), although I still hope they will fix it.

One stash at a time, doesn't have to be premium, just normal or quad stash with items. You can switch between stashes, but each time you need to modify settings.

Only identified rare and magic items, you can have other items in stash, but they won't be processed.

Pseudo mods are not supported, I may add them in future.

Depending on GGG servers load you may need to wait a bit after putting items into the stash.

GGG API limits items returned to 100 of the same type, so if you dump over 100 rings in your stash, some of them won't be processed and you won't know about it.

Jewels are not supported yet. I'm waiting for GGG to release API changes described [here](https://www.pathofexile.com/forum/view-thread/2784742/page/1#p22948552), "We will most likely move all item images to this system before 3.11.0."

## Setup
You can download a prepared executable or run from sources (just install all dependencies from requirements.txt).
After you run it for the first time, a new file "config.xml" will be created in the location of the executable and you will see a widget bar on the left edge of your screen.

![](https://i.ibb.co/qmrw6YP/main-widget.png)
![](https://i.ibb.co/tZw1kBF/widget-hidden1.png)

Buttons:
1. Allows to drag widget by the left edge, when clicked hides and shows rest of the buttons.
2. Sends request for items data, maximum once per 10 seconds. You need to have valid data in settings, described below.
3. After button 2. icon gets back from "hourglass" to "play", you can toggle on/off frames.
4. Mods list. Initial list is an example, if you don't like it, turn off the tool (last button) and replace content of filters/mods.xml with filters/mods_empty.xml or delete all mods one by one from mods list window.
You can delete mods by removing cell content and add new ones modifying default mod message at the end of each section. Each mod needs to have at least one numeric value.
5. Settings. With first run you will need to provide data to all fields, set stash type and adjust net accordingly.
Slider determines how many mods in item should have value greater or equal to your filter to be detected and have color frame.
You can modify colors in settings.xml after you exit tool, just make sure it meets QColor constructor [requirements](https://doc.qt.io/qt-5/qcolor.html).
Guide how to get session ID - [here](https://github.com/Stickymaddness/Procurement/wiki/SessionID). Remember it will change over time, so if you get error message about invalid session ID or no connection, you may need to provide new session ID.
6. Terminates tool. All settings data is saved at the moment you edit it.

Example of frames:

![](https://i.ibb.co/YccKHfH/borders.png)

Each color represents number of mods that meet requirements specified in your filter. Brown - one good mod, blue - two mods etc.

![](https://i.ibb.co/0qhjLHh/colors.png)


## Attributions
Buttons used in project were made by:
 [Freepik](https://www.flaticon.com/authors/freepik)
 [Google](https://www.flaticon.com/authors/google)
 [Becris](https://www.flaticon.com/authors/becris)
 [Pixel perfect](https://www.flaticon.com/authors/pixel-perfect)
from www.flaticon.com
