"""Small WC signs shared by public service doors; white on muted teal."""
def wc_sign(s,x,y,color):
    for ox,rows in [(0,['#...#','#...#','#.#.#','##.##','#...#']),(6,['.###','#...','#...','#...','.###'])]:
        for yy,row in enumerate(rows):
            for xx,v in enumerate(row):
                if v=='#': s.set(x+ox+xx,y+yy,color)
