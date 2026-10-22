"""The desktop app's icon: the little house with its window lit, on a round
warm tile, 32x32 (exe, taskbar, tray). No character in it on purpose
(user: Buddy's look is up to the player, so a fixed face on the icon was
wrong). tools/make_desktop_icons.py scales it up and feeds it to
`tauri icon` for every size and format."""

from pixelkit import P, Sprite

PREVIEW_SCALE = 10
SIZE = 32


def icon() -> Sprite:
    s = Sprite(SIZE, SIZE)
    # round tile: ink rim, oat face lit from the top-left
    s.ellipse(15.5, 15.5, 15.5, 15.5, P.ink[1])
    s.ellipse(15.5, 15.5, 14.5, 14.5, P.oat[2])
    s.ellipse(14.5, 14.5, 12.5, 12.5, P.oat[3])

    # walls: warm plaster, ink outline
    s.rect(7, 14, 18, 13, P.ink[1])
    s.rect(8, 15, 16, 11, P.wall_cream[2])
    s.hline(8, 23, 15, P.wall_cream[3])            # lit top edge
    s.vline(23, 16, 25, P.wall_cream[1])           # shade on the right
    s.hline(8, 23, 21, P.wall_cream[1])            # the floor between the two storeys
    # roof: a clay gable, rows widening down from the ridge
    for i, y in enumerate(range(5, 13)):
        half = 2 + i * 1.1
        x0, x1 = round(15.5 - half), round(15.5 + half) - 1
        s.hline(x0 - 1, x1 + 1, y, P.ink[1])
        s.hline(x0, x1, y, P.brick[2] if i % 2 == 0 else P.brick[3])
        s.set(x0, y, P.brick[4])                    # lit left edge
    s.hline(5, 26, 13, P.ink[1])
    s.hline(6, 25, 12, P.brick[1])                  # eave shadow
    s.rect(20, 4, 3, 5, P.ink[1]); s.rect(21, 5, 1, 4, P.brick[2])   # chimney

    # upstairs: a big window, lit warm, with a heart of light in it
    s.rect(11, 15, 10, 6, P.walnut[1])
    s.rect(12, 16, 8, 4, P.light[0])
    for dy, row in enumerate([".#.#.", "#####", ".###.", "..#.."]):
        for dx, ch in enumerate(row):
            if ch == "#":
                s.set(13 + dx, 16 + dy, P.coral[3])
    # downstairs: the door, a bush on each side
    s.rect(14, 22, 4, 5, P.ink[1]); s.rect(15, 23, 2, 4, P.sage[2])
    s.set(16, 25, P.mustard[3])
    for x in (9, 20):
        s.rect(x, 24, 3, 2, P.grass[2]); s.hline(x, x + 2, 24, P.grass[3]); s.hline(x, x + 2, 26, P.grass[1])
    # ground
    s.hline(6, 25, 27, P.ink[1])
    s.hline(8, 23, 28, P.grass[2])
    # keep everything inside the round tile: anything past the rim goes
    for y in range(SIZE):
        for x in range(SIZE):
            if (x - 15.5) ** 2 + (y - 15.5) ** 2 > 14.5 ** 2 and s.px[y, x, 3]:
                inside_rim = (x - 15.5) ** 2 + (y - 15.5) ** 2 <= 15.5 ** 2
                s.set(x, y, P.ink[1] if inside_rim else None)
    return s


def build():
    return {"app_icon": icon()}
