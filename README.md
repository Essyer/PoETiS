# PoETiS
Path of Exile Tiers in Stash tool allows you to scan your public stash for items with specified modifier values.

## Limitations

As of 13.06.2020 PoE vulcan stays on top of everything, so if you want to use vulcan and any 3rd party tool you need to run game in windowed mode (not windowed fullscreen).
Bug was already reported [here](https://www.pathofexile.com/forum/view-thread/2867255).

One stash at a time, needs to be public (you can set stash public without setting price on items). You can switch between stashes, but each time you need to modify settings.

Only identified rare and magic items, you can have other items in stash, but they won't be processed.

GGG API limits items returned to 100 of the same type, so if you dump over 100 ring to your stash some of them won't be processed and you won't know about it.

## Setup
You can download prepared executable or run from sources (just install all dependencies from requirements.txt).
After you run it for the first time, a new file "config.xml" will be created in executable location and you will see widget bar on the left edge of your screen.

![](https://i.ibb.co/qmrw6YP/main-widget.png)
![](https://i.ibb.co/vQp7wjb/main-widget-hidden.png)

Buttons:
1. Allows to drag widget by the left edge, when clicked hides and shows some buttons.
2. Sends request for items data, maximum once per 10 seconds. You need to have valid data in settings, described below.
3. After button 2. icon gets back from "hourglass" to "play", you can toggle on/off grid of rectangles.
4. Mods list. Initial list is an example, if you don't like it, turn off the tool (last button) and replace content of filters/mods.xml with filters/mods_empty.xml or delete all mods one by one.
You can delete mods by removing cell content and add new ones modifying default mod message at the end of each section. Each mod needs to have at least one numeric value.
5. Settings. With first run you will need to provide data to all fields, set stash type and adjust net accordingly.
Slider determines how many mods in item should have value from your filter to be detected and have color frame.
You can modify colors in settings.xml after you exit tool, just make sure it meets QColor constructor [requirements](https://doc.qt.io/qt-5/qcolor.html).
6. Terminates tool. All settings data is saved at the moment you edit it.

Example of frames:

![](https://i.ibb.co/YccKHfH/borders.png)

Each color represents number of modificators that meet requirements specified in your filter. Brown - one good mod, blue - two mods etc.

![](https://i.ibb.co/0qhjLHh/colors.png)

