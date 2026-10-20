"""The desktop app's icon: Buddy's head and shoulders on a round warm tile,
32x32 (exe, taskbar, tray). tools/make_desktop_icons.py scales it up and
feeds it to `tauri icon` for every size and format."""

from pixelkit import P, Sprite

import doll

PREVIEW_SCALE = 10
SIZE = 32


def icon() -> Sprite:
    s = Sprite(SIZE, SIZE)
    # round tile: ink rim, oat face lit from the top-left
    s.ellipse(15.5, 15.5, 15.5, 15.5, P.ink[1])
    s.ellipse(15.5, 15.5, 14.5, 14.5, P.oat[2])
    s.ellipse(14.5, 14.5, 12.5, 12.5, P.oat[3])
    body = doll.GIRL.render(expr="happy")
    bust = Sprite(doll.W, 22)
    bust.blit(body, 0, 0)                      # head and shoulders
    s.blit(bust, 6, 7)
    # keep the bust inside the round tile: anything past the rim goes
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - 15.5) ** 2 + (y - 15.5) ** 2 > 14.5 ** 2 and s.px[y, x, 3]:
                inside_rim = (x - 15.5) ** 2 + (y - 15.5) ** 2 <= 15.5 ** 2
                s.set(x, y, P.ink[1] if inside_rim else None)
    return s


def build():
    return {"app_icon": icon()}
