"""栗尾市 interiors. Same floor and furniture coordinates as the home controller."""
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw
from pixelkit import P
from infei_bed_covers import cover

ROOM = Path(__file__).resolve().parents[2] / 'out/concept/autumn_detective_inside.png'
GUEST_QUILT = ['#817361', '#9e9280', '#cbbfae', '#e2d8c9', '#f3ede3']
RESIDENT_QUILT = ['#59616e', '#777c84', '#a1a9b0', '#c3c8ca', '#e0e0d9']


def recolor(room, bounds, colors):
    palette = {ImageColor.getrgb(k): ImageColor.getrgb(v) for k, v in colors.items()}
    patch = room.crop(bounds)
    patch.putdata([palette.get(p, p) for p in patch.getdata()])
    room.paste(patch, bounds[:2])


def interiors():
    base = Image.open(ROOM).convert('RGB')
    office, hotel = base.copy(), base.copy()
    hotel.paste(hotel.crop((130,33,131,53)).resize((43,20),Image.Resampling.NEAREST),(84,33))
    # A subdued office at street level, warm walls and pale trim in the inn.
    recolor(office,(7,63,211,109),{'#a89a8a':P.sea_grey[2],'#7d7266':P.slate[1]})
    recolor(hotel,(7,6,210,109),{'#a89a8a':P.wall_cream[3],'#7d7266':P.teal[1],
                              '#6b4a37':P.wood[3],'#4a3329':P.wood[2],'#8c6648':P.wood[4]})
    recolor(office,(98,38,125,48),dict(zip(GUEST_QUILT[2:],RESIDENT_QUILT[2:])))

    def paint(room):
        d=ImageDraw.Draw(room)
        def box(x,y,w,h,tone):
            d.rectangle((x,y,x+w-1,y+h-1),fill=tone)
        return box

    box=paint(office)
    # Filing cabinet and a dated case board behind the desk.
    box(104,77,20,30,P.slate[0]);box(105,78,18,2,P.steel[3])
    for y in (81,89,97):
        box(105,y,18,7,P.steel[2]);box(106,y,16,1,P.steel[3])
        box(111,y+2,6,2,P.steel[0]);box(112,y+2,4,1,P.mustard[2])
    box(159,67,32,13,P.walnut[0]);box(160,68,30,11,P.oat[2])
    for x,y in ((162,70),(171,72),(182,69)):
        box(x,y,6,6,P.linen[3]);box(x+2,y+2,3,1,P.oat[1]);box(x+2,y,1,1,P.clay[2])
    box(160,94,11,2,P.wall_cream[3]);box(168,93,9,2,P.oat[3])
    box(179,92,9,3,P.walnut[1]);box(180,92,7,1,P.wall_cream[3])
    box(158,103,9,2,P.mustard[2]);box(185,103,8,2,P.mustard[2])

    box=paint(hotel)
    # Luggage upstairs, brass bell and room keys downstairs.
    box(90,42,31,7,P.wood[0]);box(91,41,29,5,P.teal[1]);box(92,41,27,1,P.teal[3])
    box(95,35,12,8,P.walnut[0]);box(96,36,10,6,P.oat[1]);box(99,34,4,2,P.wood[1])
    box(110,37,8,5,P.teal[0]);box(111,38,6,3,P.teal[2])
    box(153,83,15,13,P.wall_cream[3]);box(153,94,18,3,P.wood[2])
    box(157,89,7,4,P.mustard[2]);box(159,88,3,1,P.mustard[3]);box(156,93,9,1,P.walnut[0])
    box(151,101,18,5,P.teal[1]);box(176,101,18,5,P.teal[1])
    box(177,71,16,12,P.teal[0]);box(178,72,14,10,P.wood[3])
    for x in (180,184,188):
        box(x,74,2,2,P.mustard[3]);box(x+1,76,1,3,P.mustard[1])
    box(26,40,24,6,P.teal[1]);box(26,40,24,1,P.teal[3]);box(26,46,24,2,P.teal[0])
    for x in range(28,50,4):box(x,42,2,1,P.teal[3])
    return office,hotel


def sleep_overlays():
    return [cover(44,quilt).to_image() for quilt in (GUEST_QUILT,RESIDENT_QUILT,P.teal)]
