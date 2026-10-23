"""Park services at house scale: 3/4-view WC and a warm oden yatai.
Top-left light; front/top/side planes use distinct palette shades. Both
stand on raised stone pads behind the public walking lane (y=103).
"""
from pixelkit import P, Sprite


def poly(s, points, color):
    """Integer scanlines keep small oblique planes crisp, with no antialiasing."""
    for y in range(min(p[1] for p in points), max(p[1] for p in points) + 1):
        xs = []
        for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
            if y0 == y1:
                if y == y0:
                    xs.extend((x0, x1))
            elif min(y0, y1) <= y <= max(y0, y1):
                xs.append(round(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
        if xs:
            s.hline(min(xs), max(xs), y, color)


def restroom(s):
    # Ground contact and three ascending stone steps.
    s.ellipse(275, 94, 50, 5, P.grass[0])
    poly(s, [(227,90),(307,90),(320,85),(320,91),(307,97),(227,97)], P.pave[1])
    for y, left, right in ((90,235,308),(93,231,312),(96,227,316)):
        s.hline(left, right, y, P.pave[4]).hline(left, right, y + 1, P.pave[2])
    # Plaster front and a cool, receding right wall.
    s.rect(235, 43, 66, 47, P.plaster_bath[2])
    poly(s, [(301,43),(316,36),(316,83),(301,90)], P.plaster_bath[0])
    s.vline(235,43,89,P.plaster_bath[3]).vline(300,43,89,P.pave[1])
    for y in (51,77,85):
        s.hline(236,299,y,P.plaster_bath[1])
        s.line(302,y,315,y-6,P.pave[1])
    # Deep door recess, wood frame, and two louvered transom windows.
    s.rect(259, 55, 23, 35, P.walnut[0]).rect(261,57,19,32,P.teal[1])
    s.vline(261,57,88,P.teal[3]).hline(261,279,57,P.teal[4])
    s.rect(264,60,13,10,P.glass[0]).rect(265,61,11,8,P.glass[2])
    for x in (268,273):
        s.vline(x,61,68,P.teal[1])
    s.rect(276,76,2,2,P.mustard[3]).hline(263,277,86,P.teal[0])
    for x in (241,286):
        s.rect(x,57,9,12,P.pave[0]).rect(x+1,58,7,10,P.glass[1])
        for y in (60,63,66):
            s.hline(x+1,x+7,y,P.plaster_bath[2])
    # Pitched roof with a visible top, fascia and deep eave shadow.
    poly(s, [(230,40),(243,27),(306,27),(321,37),(300,45)], P.slate[2])
    poly(s, [(230,40),(243,27),(306,27),(294,40)], P.slate[3])
    for x in range(245,302,7):
        s.line(x,28,x-10,39,P.slate[1])
    poly(s, [(230,40),(300,40),(321,32),(321,37),(301,46),(230,46)], P.slate[0])
    s.hline(230,300,40,P.slate[4]).line(301,40,321,32,P.slate[3])
    s.rect(237,46,62,3,P.pave[0])
    # A sign with readable WC letters and simple person pictograms.
    s.rect(250,47,37,9,P.teal[0]).rect(251,48,35,7,P.teal[2])
    for ox, rows in [(258,['#...#','#.#.#','#.#.#','.###.']), (267,['.###.','#....','#....','.###.'])]:
        for yy,row in enumerate(rows):
            for xx,c in enumerate(row):
                if c=='#': s.set(ox+xx,49+yy,P.linen[3])
    for x, skirt in ((244,False),(290,True)):
        s.rect(x,72,2,2,P.teal[2]).rect(x-1,75,4,3,P.teal[2])
        if skirt: s.hline(x-2,x+3,78,P.teal[2])
        s.vline(x,78,81,P.teal[2]).vline(x+2,78,81,P.teal[2])
    for x in (230,309):
        s.rect(x-3,86,8,5,P.clay[1]).hline(x-3,x+4,85,P.clay[3])
        s.ellipse(x,82,6,5,P.sage[1]).ellipse(x-1,80,4,3,P.sage[3])
    # Wall-mounted warm lantern, carried into the emissive pass at night.
    s.rect(298,52,4,7,P.steel[0]).rect(299,53,2,4,P.light[0])


def oden_front(s):
    # Raised counter: lit top, dark front, visible oblique right panel.
    poly(s,[(123,77),(205,77),(222,70),(139,70)],P.oak[3])
    s.rect(123,78,82,17,P.walnut[1])
    poly(s,[(205,78),(222,71),(222,89),(205,96)],P.walnut[0])
    for x in range(127,203,9):
        s.rect(x,81,6,11,P.oak[1]).vline(x,81,91,P.oak[2])
    s.hline(122,205,77,P.oak[4]).hline(123,204,79,P.walnut[0])
    s.hline(123,204,94,P.walnut[0])
    for x in (130,197):
        s.rect(x,95,4,4,P.walnut[0])
    # Stainless oden pan, six compartments with distinct food shapes.
    poly(s,[(145,75),(183,75),(190,70),(152,70)],P.metal[4])
    s.rect(147,72,36,3,P.mustard[1]).hline(147,183,75,P.metal[2])
    for x in (158,171): s.vline(x,71,74,P.metal[3])
    s.hline(149,185,72,P.metal[3])
    s.rect(151,71,4,2,P.sand[4]).hline(162,166,73,P.sand[3])
    s.set(176,71,P.sand[4]).set(177,72,P.sand[2])
    s.rect(172,73,4,1,P.clay[2])
    s.ellipse(191,74,4,1,P.porcelain[3]).hline(188,192,76,P.porcelain[1])
    s.rect(199,68,3,7,P.walnut[1]).vline(199,66,70,P.oak[3]).vline(201,65,69,P.oak[3])


def oden(s):
    s.ellipse(176,97,63,6,P.grass[0])
    poly(s,[(112,92),(210,92),(228,85),(230,94),(211,101),(110,101)],P.pave[1])
    poly(s,[(110,95),(211,95),(230,88),(230,91),(211,99),(110,99)],P.pave[3])
    # Back wall and side display create an enclosed, warm little workspace.
    s.rect(130,48,72,29,P.walnut[0]).rect(133,50,65,26,P.clay[0])
    poly(s,[(202,49),(216,42),(216,73),(202,80)],P.walnut[1])
    s.rect(135,61,60,3,P.oak[2])
    for x in range(139,192,8):
        s.rect(x,55,4,6,P.porcelain[2]).hline(x,x+3,55,P.porcelain[3])
    for x in (125,201):
        s.rect(x,43,4,50,P.walnut[1]).vline(x,43,92,P.oak[3])
    # Gabled canvas roof: pale lit top and a muted indigo shaded plane.
    poly(s,[(114,45),(134,32),(214,32),(228,42),(206,51)],P.blue[1])
    poly(s,[(114,45),(134,32),(214,32),(196,45)],P.blue[2])
    for x in range(133,209,10):
        s.line(x,34,x-14,44,P.blue[3])
    s.hline(113,205,45,P.linen[2]).line(206,45,228,36,P.blue[1])
    poly(s,[(114,46),(206,46),(228,37),(228,42),(206,52),(114,52)],P.walnut[0])
    # Three short noren curtains; hand-pixel signs suggest a Japanese yatai.
    signs = [
        [".#...#.","..#.#..",".......","#######","...#...","#######","..#.#..",".#...#."],
        ["..#....","#######","..#....",".#####.","....#..","..#.#.#",".#..#..","...##.."],
        ["..#.#..","#######","..#.#..","#######",".#.....","..####.","..#..#.","..####.",".#.#.#."],
    ]
    for x, glyph in zip((137,154,171),signs):
        s.rect(x,50,15,11,P.blue[1]).vline(x,50,59,P.blue[3])
        for yy,row in enumerate(glyph):
            for xx,c in enumerate(row):
                if c == "#": s.set(x+4+xx,51+yy,P.linen[2])
    for x in (117,213):
        s.vline(x,46,51,P.walnut[0])
        s.ellipse(x,59,5,8,P.clay[0]).ellipse(x-1,58,4,7,P.coral[2])
        for y in (53,57,61,64): s.hline(x-3,x+3,y,P.clay[1])
        s.hline(x-2,x+2,51,P.mustard[2]).hline(x-2,x+2,67,P.walnut[0])
    oden_front(s)
    # Low round stools, in front of the counter, with angled legs.
    for x in (147,177,201):
        s.line(x-3,96,x-5,103,P.walnut[0]).line(x+3,96,x+5,103,P.walnut[0])
        s.ellipse(x,95,6,2,P.walnut[1]).ellipse(x,94,6,1,P.oak[3])
