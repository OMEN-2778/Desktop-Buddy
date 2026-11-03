"""任务 icons (owner 2026-11-03: "make more icons for quests, they'll be useful later").
16x16, shown at 2x in the 任务 panel like the farm icons: light from the top-left, every part
outlined in the darkest shade of its own ramp. One icon per kind of errand or story beat."""

from pixelkit import P, Sprite

PREVIEW_SCALE = 8


def g(rows, legend):
    assert len(rows) == 16 and all(len(r) <= 16 for r in rows), [len(r) for r in rows]
    return Sprite.from_grid("\n".join(r.ljust(16, ".") for r in rows), legend)


R, Y, B, GR, K, O = P.coral, P.mustard, P.blue, P.green, P.slate, P.oak
W = P.snow + [P.light[1]]     # white things (rabbit, steam, tower): 5 steps
L = P.sand                    # paper: scroll, letter, map, book pages
_ = "................"

ICONS = {
 "scroll": ([_, ".oooooooooooooo.", "ossWWWWWWWWWWsso", ".oooooooooooooo.",
             "..oWpppppppppo..", "..opllllllpppo..", "..oppppppppppo..", "..opllllllllpo..",
             "..oppppppppppo..", "..oplllllprrro..", "..opppppprRRro..", "..oppppppprrro..",
             ".oooooooooooooo.", "ossWWWWWWWWWWsso", ".oooooooooooooo.", _],
            {"o": O[0], "s": O[2], "W": O[3], "p": L[3], "l": L[1], "r": R[2], "R": R[1]}),
 "letter": ([_, _, _, ".oooooooooooooo.", ".oPoPPPPPPPPoPo.", ".oPPoPPPPPPoPPo.", ".oPPPoPPPPoPPPo.",
             ".oPPPPorroPPPPo.", ".oPPPPrWRrPPPPo.", ".oPPPoPrrPoPPPo.", ".oPPoPPPPPPoPPo.", ".oPoPPPPPPPPoPo.",
             ".oSSSSSSSSSSSSo.", ".oooooooooooooo.", _, _],
            {"o": L[0], "P": L[3], "S": L[2], "r": R[2], "R": R[1], "W": R[4]}),
 "windmill": (["...o.......o....", "...oso....oso...", "....oso..oso....", ".....osooso.....", "......owwo......",
               ".....osooso.....", "....oso.ooso....", "...oso.owwoso...", "...oo..owwo.oo..", ".......owwwo....",
               "......owwwwo....", "......owdwwo....", "......owdwwo....", ".....oooooooo...", "....ggggggggg...", _],
              {"o": K[0], "s": O[3], "w": W[3], "d": O[1], "g": GR[2]}),
 "suona": (['................', '................', '................', '................', '...........ooo..', '..........oYWYo.', '.o.......oYWYYDo', 'oRooooooooYYYYDo', 'oRwwdwwdwwYYYYDo', 'oRooooooooYYYYDo', '.o.......oDYYDDo', '..........oDDDo.', '...........ooo..', '................', '................', '................'],
           {"o": Y[0], "Y": Y[3], "W": Y[4], "D": Y[1], "R": R[2], "w": O[3], "d": O[0]}),
 "footprints": ([_, "..........oo.o..", ".........obbobo.", "..........oo.o..", ".........oooo...",
                 "........obbbbo..", "........obbbbo..", "...oo.o..obbo...", "..obbobo..oo....", "...oo.o.........",
                 "..oooo..........", ".obbbbo.........", ".obbbbo.........", "..obbo..........", "...oo...........", _],
                {"o": O[0], "b": O[2]}),
 "rabbit": (["...oo...oo......", "..owwo.owwo.....", "..owpo.owpo.....", "..owpo.owpo.....", "..owwoowwwo.....",
             "...owwwwwwoo....", "..owwwwwwwwwo...", "..owkwwwwkwwo...", "..owwwwwwwwwo...", "..owpwwRwwpwo...",
             "...owwwwwwwo....", "..oowwwwwwwoo...", ".owwwwwwwwwwwo..", ".oSwwwwwwwwwSo..", "..ooooooooooo...", _],
            {"o": K[1], "w": W[4], "S": W[2], "p": R[3], "k": K[0], "R": R[2]}),
 "stew": ([_, "....s...s...s...", ".....s...s...s..", "....s...s...s...", _, "..oooooooooooo..",
           ".oCCWCCCCCCCCDo.", "oCCCCCCCCCCCCDDo", "oooooooooooooooo", ".oCWCCCCCCCCCDo.", ".oCCCCCCCCCCCDo.",
           ".oCCCCCCCCCCDDo.", "..oCCCCCCCCDDo..", "...oooooooooo...", _, _],
          {"o": P.clay[0], "C": P.clay[2], "W": P.clay[4], "D": P.clay[1], "s": W[2]}),
 "heart": ([_, _, _, "...ooo...ooo....", "..oHWCo.oCCCo...", "..oHCCCoCCCDo...", "..oCCCCCCCCDo...",
            "...oCCCCCCDo....", "....oCCCCDo.....", ".....oCCDo......", "......oDo.......", ".......o........", _, _, _, _],
           {"o": R[0], "C": R[2], "H": R[3], "W": R[4], "D": R[1]}),
 "lantern": (["......oo........", ".....oYYo.......", "...oooooooo.....", "..oRRRRRRRRo....", ".oRWRRRRRRRDo...",
              ".oRWRRRRRRRDo...", ".oRRRRRRRRRDo...", ".oRRRRRRRRRDo...", ".oRRRRRRRRDDo...", "..oRRRRRRRDo....",
              "...oooooooo.....", ".....oYYo.......", "....oY.Yo.......", "....Y.Y.Y.......", "....Y...Y.......", _],
             {"o": R[0], "R": R[2], "W": R[4], "D": R[1], "Y": Y[2]}),
 "key": ([_, _, "...oooo.........", "..oYWYYo........", ".oYWooYYo.......", ".oYo..oYo.......", ".oYo..oYo.......",
          ".oYYooYYoooooooo", "..oYYYYDYYYYYYYo", "...ooooDoooDoDoo", ".........oDo.oo.", "..........o.....", _, _, _, _],
         {"o": Y[0], "Y": Y[3], "W": Y[4], "D": Y[1]}),
 "map": ([_, _, ".ooooooooooooo..", ".oMMMoGGGGoMMMo.", ".oMWMoGGGGoMMMo.", ".oMMMoGGBGoMRMo.",
          ".oMMMoGBBGoMRMo.", ".oMlMoGGBGoMMMo.", ".oMMloGGGGoMMMo.", ".oMMMoGGGGolMMo.", ".oMMMoGGGlolMMo.",
          ".oMMMoGGGGoMMMo.", ".ooooooooooooo..", _, _, _],
         {"o": O[0], "M": L[3], "W": L[4], "G": P.sage[3], "B": B[3], "R": R[2], "l": O[2]}),
 "seedling": ([_, "...ooo..ooo.....", "..oGGGooGGGo....", "..oGWGGoGGGo....", "...oGGGGGGo.....", ".....ooGoo......",
               ".......Go.......", ".......Go.......", ".......Go.......", "...ooooGoooo....", "..oSSSSSSSSSo...",
               ".oSdSSSSSSdSSo..", ".oSSSSdSSSSSSo..", ".ooooooooooooo..", _, _],
              {"o": GR[0], "G": GR[3], "W": GR[4], "S": O[2], "d": O[1]}),
 "basket": ([_, _, "....oooooo......", "...o......o.....", "..o.ooo....o....", "..ooRRoooGGoo...",
             ".oRRWRoGGGWGo...", ".ooooooooooooo..", ".oBBbBBbBBbBBo..", ".oBbBBbBBbBBbo..", ".oBBbBBbBBbBBo..",
             "..oBbBBbBBbBo...", "...ooooooooo....", _, _, _],
            {"o": O[0], "R": R[2], "W": R[4], "G": GR[3], "B": O[3], "b": O[2]}),
 "fish": ([_, _, _, ".....oooooo.....", "...ooBBBBBBoo.o.", "..oBWkBBBBBBBoBo", ".oBBBBBBBBBBBBBo",
           ".oBBBBBBBBBBBoBo", "..oDBBBBBBBBDo.o", "...ooDDDDDDoo...", ".....oooooo.....", _, _, _, _, _],
          {"o": B[0], "B": B[3], "W": B[4], "D": B[1], "k": K[0]}),
 "moon": ([_, "....oooo........", "...oYYYYo.....o.", "..oYWYYoo....oWo", ".oYWYYo.......o.", ".oYYYo..........",
           ".oYYYo.....o....", ".oYYYo....oWo...", ".oYYYYo....o....", ".oYYYYYo........", "..oYYYYYooo.....",
           "...oYYYYYYYo....", "....ooooooo.....", _, _, _],
          {"o": Y[0], "Y": Y[3], "W": Y[4]}),
 "phone": ([_, "....oooooooo....", "...oSSSSSSSSo...", "...oSooooooSo...", "...oSoBBBBoSo...", "...oSoBWBBoSo...",
            "...oSoBBBBoSo...", "...oSoBBBBoSo...", "...oSoBBBBoSo...", "...oSoooooo So..".replace(" ", "o"),
            "...oSSSooSSSo...", "...oSSSSSSSSo...", "....oooooooo....", _, _, _],
           {"o": K[0], "S": K[3], "B": B[3], "W": B[4]}),
 "flower": ([_, ".....oo.oo......", "....oPPoPPo.....", "....oPWPPPo.....", "..oooPPoPPooo...", ".oPPPoYYYoPPPo..",
             ".oPWPoYWYoPPPo..", ".oPPPoYYYoPPPo..", "..oooPPoPPooo...", "....oPPoPPo.....", ".....oo.oo......",
             ".......Go.......", "......oGGoo.....", ".....oGGo.......", ".......Go.......", _],
            {"o": R[0], "P": R[3], "W": R[4], "Y": Y[3], "G": GR[2]}),
 "note": ([_, "......oooooooo..", "......oNNNNNNo..", "......oNoooooo..", "......oNo....oo.", "......oNo...oNo.",
           "......oNo...oNo.", "......oNo...oNo.", "...oooNNo...oNo.", "..oNNNNNo.oooNo.", "..oNWNNNooNNNNo.",
           "..oNNNNDooNWNDo.", "...oooooooNNDo..", "..........ooo...", _, _],
          {"o": P.lilac[0], "N": P.lilac[2], "W": P.lilac[3], "D": P.lilac[1]}),
 "book": ([_, _, "..ooooooo.ooooo.", ".oWWWWWWoTTTTTo.", ".oWllllWoTllllTo".replace("T", "W", 2)[:16],
           ".oWWWWWWoWWWWWo.", ".oWlllWWoWllllo.", ".oWWWWWWoWWWWWo.", ".oWllllWoWlllWo.", ".oWWWWWWoWWWWWo.",
           ".oCCCCCCoCCCCCo.", "..ooooooooooooo.", _, _, _, _],
          {"o": B[0], "W": L[4], "T": L[4], "l": L[1], "C": B[2]}),
 "cake": ([_, "........o.......", ".......oYo......", "........o.......", "........R.......", "....oooRooooo...",
           "...oPPPPPPPPPo..", "...oPWPPRPPPPo..", "...oRRRRRRRRRo..", "...oCCCCCCCCCo..", "...oCWCCCCCCDo..",
           "...oPPPPPPPPPo..", "..ooooooooooooo.", ".oSSSSSSSSSSSSSo", "..ooooooooooooo.", _],
          {"o": O[0], "P": L[4], "W": W[4], "R": R[2], "C": O[3], "D": O[2], "Y": Y[3], "S": W[2]}),
 "star": ([_, ".......oo.......", "......oYYo......", "......oYYo......", ".....oYWYYo.....", "ooooooYWYYoooooo",
           "oYYYYYYYYYYYYYDo", ".oYYYYYYYYYYYDo.", "..oYYYYYYYYYDo..", "...oYYYYYYYDo...", "...oYYYDYYYDo...",
           "..oYYYDooDYYDo..", "..oYYDo..oDYDo..", ".oYDoo....ooDDo.", ".ooo........ooo.", _],
          {"o": Y[0], "Y": Y[3], "W": Y[4], "D": Y[1]}),
 "smile": ([_, ".....oooooo.....", "...ooyyyyyyoo...", "..oyWyyyyyyyYo..", "..oyyoyyyyoyYo..", ".oyyyoyyyyoyyYo.",
            ".oyyyyyyyyyyyYo.", ".oyyoyyyyyyoyYo.", ".oyyyooooooyyYo.", ".oyyyoRRRRoyyYo.", "..oyyyoRRoyyYo..",
            "..oYyyyooyyYYo..", "...ooYYYYYYoo...", ".....oooooo.....", _, _],
           {"o": Y[0], "y": Y[3], "W": Y[4], "Y": Y[2], "R": R[2]}),
 "drop": ([_, ".......oo.......", "......obbo......", ".....obbbbo.....", "....obbbbbbo....", "....obWbbbbo....",
           "...obWbbbbbbo...", "...obbbbbbbBo...", "...obbbbbbbBo...", "...obbbbbbBBo...", "....obbbbBBo....",
           ".....oBBBBo.....", "......oooo......", _, _, _],
          {"o": B[0], "b": B[3], "W": B[4], "B": B[2]}),
 "lens": ([_, "....oooo........", "...okkkko.......", "..okwkkkko......", ".okwkkkkkko.....", ".okkkkkkkko.....",
           ".okkkkkkkko.....", ".okkkkkkkko.....", "..okkkkkKo......", "...okkKKoo......", "....oooooOo.....",
           ".........oOOo...", "..........oOOo..", "...........oo...", _, _],
          {"o": K[0], "k": K[4], "w": W[4], "K": K[3], "O": O[2]}),
 "gift": ([_, ".....oo..oo.....", "....orro.orro...", ".....orroRro....", "..ooooooooooo...", "..orrrrrRrrro...",
           "..ooooooooooo...", "...oggggRgggo...", "...ogwggRgggo...", "...oggggRgggo...", "...oggggRggGo...",
           "...oggggRgGGo...", "...ooooooooo....", _, _, _],
          {"o": GR[0], "g": GR[3], "w": GR[4], "G": GR[2], "r": R[2], "R": R[1]}),
 "house": (['................', '.......oo.......', '......orro......', '.....orrrro.....', '....orrrrrro....', '...orrrrrrrro...', '..oooooooooooo..', '...oppppppppo...', '...opllpdddpo...', '...opllpdddpo...', '...oppppdYdpo...', '...oppppdddpo...', '...oooooooooo...', '................', '................', '................'],
           {"o": O[0], "r": R[2], "p": L[3], "l": B[3], "Y": Y[3], "d": O[2]}),
}


def build():
    out = {}
    for name, (rows, legend) in ICONS.items():
        out[f"quest_icon_{name}"] = g(rows, legend)
    return out
