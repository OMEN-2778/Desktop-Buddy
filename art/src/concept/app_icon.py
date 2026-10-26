"""Desktop icon: the exact house sticker used by the return-home transition.

Only transparent padding is added to make the 36x32 sticker square. Keeping
one drawing source prevents the EXE/taskbar/tray house from drifting apart.
"""
from pixelkit import Sprite
from trip_icons import home

PREVIEW_SCALE = 10
SIZE = 36


def icon() -> Sprite:
    house = home()
    return house.pad(0, 2, 0, 2)


def build():
    return {"app_icon": icon()}
