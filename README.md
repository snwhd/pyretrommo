# retrotracker
stats tracker for https://retro-mmo.com/play

Uses OCR to watch screen and parse battle events. Keeps track of damage,
gold and experience.

Only tested on Linux (Debian)

## executables
There are 4 executable python scripts for using retrotracker:
1. guitracker.py - visual interface, does not support all features yet
1. retrotracker.py - command line tracker
1. modify.py - queries for editing the database
1. query.py - read-only database queries

## basic usage
1. install some prereqs
    1. python3 tesseract and sqlite3 (`apt install tesseract-ocr python3 sqlite3`)
        1. [python](https://python.org)
        1. [tesseract](https://tesseract-ocr.github.io/tessdoc/Home.html#binaries)
        1. [sqlite](https://sqlite.org/download.html)
    1. python libraries: `python3 -m pip install numpy pillow pytesseract pyscreenshot unidecode PyQt5 jellyfish`
1. start by initializing the database: `./modify.py create`
1. create some player stats
    1. use preset stats `./modify create_presets`
    1. or use the interactive tool `./modify add_player`
    1. you can then convirm your player with `./query players`
    1. NOTE: not all item stats are in this tool yet, but adding them is easy!
(check the HGear, BGear, OGear, and MGear enums in player.py).
1. run the tracker `./retrotracker.py start --position "retrommo username" "stats alias"`
    1. see note below on positioning
    1. stats alias was created in step 3 above


## positioning
The OCR needs to read battle text. Using `--position` with retrotracker start
will prompt you to input the screen positions. It does this by detecting
your mouse position at two points: top left and bottom right of the text box.

The optimal positioning here will create a rectangle that contains only the
text, and NOT the pixel border around the text. The border can mess up text
recognition. See the screenshot below for refernce:

![positioning guide](res/screen_position.png "positioning guide")

Note: you have to press enter on the terminal before it reads your input.
Use alt-tab since you can't move the mouse until it has read the position!

## work in progress

* fixing OCR typos with known retrommo names (items, monsters, abilities...)
* maybe a gui interface or something, rightn now CLI only
