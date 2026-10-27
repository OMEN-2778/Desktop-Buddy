"""Pet art study, independent of adoption/gameplay. All sprites are 32x28.

Camera: the same shallow side/front view as Buddy; feet at y=25. Lighting
comes from upper left. Cats share one rig; coats never alter their geometry.
Dogs vary torso, legs, muzzle, ear and tail geometry. No random drawing.
"""
from dataclasses import dataclass

from pixelkit import P, Sprite

W, H, FEET = 32, 28, 25
PREVIEW_SCALE = 6
FUR = {
    'white': (P.cut[0], P.oat[1], P.linen[2], P.linen[3], P.linen[3]),
    'cream': tuple(P.oat),
    'ginger': (P.clay[0], P.clay[1], P.clay[2], P.clay[3], P.birch[3]),
    'cat_ginger': (P.hair_brown[0], P.hair_brown[1], P.hair_brown[3], P.birch[2], P.birch[3]),
    'gold': tuple(P.birch) + (P.birch[-1],),
    'brown': tuple(P.hair_brown),
    'black': tuple(P.hair_black),
    'blue': (P.cut[0], P.metal[1], P.metal[2], P.metal[3], P.linen[2]),
    'silver': (P.cut[0], P.metal[2], P.metal[3], P.linen[2], P.linen[3]),
    'chocolate': tuple(P.walnut),
}


@dataclass(frozen=True)
class Breed:
    id: str
    name: str
    species: str
    color: str
    pattern: str = 'solid'
    body: int = 6
    height: int = 4
    legs: int = 4
    head: int = 4
    ear: str = 'point'
    tail: str = 'long'


BREEDS = [
    Breed('orange', '田园橘猫', 'cat', 'ginger', 'tabby'),
    Breed('tabby', '狸花猫', 'cat', 'brown', 'tabby'),
    Breed('calico', '三花猫', 'cat', 'white', 'calico'),
    Breed('cow', '奶牛猫', 'cat', 'white', 'cow'),
    Breed('black', '黑猫', 'cat', 'black'),
    Breed('white', '白猫', 'cat', 'white'),
    Breed('british_blue', '英短蓝猫', 'cat', 'blue'),
    Breed('silver', '英短银渐层', 'cat', 'silver', 'gradient'),
    Breed('american_tabby', '美短银虎斑', 'cat', 'silver', 'tabby'),
    Breed('siamese', '暹罗猫', 'cat', 'cream', 'point'),
    Breed('ragdoll', '布偶猫', 'cat', 'white', 'bicolor'),
    Breed('tortoiseshell', '玳瑁猫', 'cat', 'black', 'tortie'),
    Breed('corgi', '柯基', 'dog', 'ginger', 'bib', 7, 4, 2, 4, 'large', 'stub'),
    Breed('shiba', '柴犬', 'dog', 'ginger', 'bib', 6, 4, 4, 4, 'point', 'curl'),
    Breed('golden', '金毛', 'dog', 'gold', 'solid', 7, 5, 5, 5, 'flop', 'feather'),
    Breed('labrador', '拉布拉多', 'dog', 'chocolate', 'solid', 7, 5, 5, 5, 'flop', 'long'),
    Breed('husky', '哈士奇', 'dog', 'blue', 'mask', 7, 5, 5, 5, 'point', 'fluffy'),
    Breed('samoyed', '萨摩耶', 'dog', 'white', 'solid', 7, 6, 4, 5, 'point', 'curl'),
    Breed('bichon', '比熊', 'dog', 'white', 'solid', 5, 4, 3, 5, 'round', 'puff'),
    Breed('poodle', '泰迪', 'dog', 'brown', 'solid', 5, 4, 4, 4, 'round', 'puff'),
    Breed('border_collie', '边牧', 'dog', 'black', 'blaze', 7, 4, 5, 4, 'fold', 'feather'),
    Breed('shepherd', '德牧', 'dog', 'brown', 'saddle', 7, 5, 6, 5, 'large', 'long'),
    Breed('dachshund', '腊肠', 'dog', 'chocolate', 'tan', 9, 3, 2, 4, 'flop', 'thin'),
    Breed('beagle', '比格', 'dog', 'gold', 'saddle', 6, 4, 4, 4, 'flop', 'long'),
]

# Duration is per-frame milliseconds. Different actions have real key poses,
# not a renamed idle clip. Locomotion can later synchronize to world distance.
COMMON_ACTIONS = {
    'idle': ('站立呼吸', 4, 260), 'blink': ('眨眼', 4, 160),
    'walk': ('慢走', 6, 140), 'run': ('小跑', 6, 90),
    'sit_down': ('坐下', 4, 150), 'sit': ('坐着等', 4, 280),
    'stand_up': ('起身', 4, 150), 'lie_down': ('趴下', 4, 170),
    'rest': ('趴着观察', 4, 300), 'sleep': ('蜷着睡觉', 4, 420),
    'wake': ('睡醒抬头', 6, 170), 'eat': ('低头吃饭', 6, 150),
    'drink': ('低头喝水', 6, 140), 'sniff': ('低头嗅闻', 6, 180),
    'look': ('左右张望', 6, 240), 'groom': ('舔毛', 6, 180),
    'scratch': ('后腿抓痒', 6, 120), 'stretch': ('伸懒腰', 6, 210),
    'play': ('伏低玩耍', 6, 150), 'happy': ('开心回应', 6, 140),
    'nuzzle': ('低头蹭蹭', 6, 200), 'roll': ('翻身打滚', 8, 160),
    'curious': ('好奇歪头', 6, 240), 'content': ('眯眼满足', 6, 260),
    'drowsy': ('困倦眨眼', 6, 280), 'surprised': ('惊讶抬头', 6, 210),
    'shake': ('抖抖身体', 6, 100),
}
SPECIES_ACTIONS = {
    'cat': {'knead': ('交替踩奶', 6, 210), 'pounce': ('蓄力扑跃', 6, 130)},
    'dog': {'wag': ('摇尾巴', 6, 130), 'pant': ('吐舌喘气', 6, 180), 'bark': ('张嘴叫', 4, 150)},
}
DIRECTIONS = ('right', 'left', 'front', 'back')


def actions(species):
    return {**COMMON_ACTIONS, **SPECIES_ACTIONS[species]}


def coat(b, part, dx, dy, rx, ry):
    """Color-only markings in local part coordinates; never mutate silhouettes."""
    base = b.color
    p = b.pattern
    if p == 'tabby':
        if part=='body':
            # Broken, curved ribs following the flank, not straight zebra bars.
            offset={-4:0,-3:-1,-2:-1,-1:0,0:1,1:1,2:0,3:-1}.get(dy,0)
            centers=(-4,0,4) if dy<1 else (-3,3)
            if -ry<dy<ry-1 and any(abs(dx-c-offset)<=(1 if dy in (-2,0) else 0) for c in centers):return FUR['cat_ginger' if base=='ginger' else base],-1
        elif part=='head' and (dy in (-4,-3) and abs(dx) in (1,3) or dy==-2 and abs(dx)==2):return FUR['cat_ginger' if base=='ginger' else base],-1
    if p == 'calico':
        if (part=='body' and (dx+3)**2/14+(dy+1)**2/7<1) or (part=='head' and (dx+3)**2/9+(dy+1)**2/12<1):
            base = 'ginger'
        elif (part=='body' and (dx-4)**2/8+(dy+1)**2/6<1) or (part=='head' and (dx-3)**2/5+(dy+3)**2/8<1):
            base = 'black'
    elif p == 'cow' and ((part == 'body' and (dx + 2) ** 2 + (dy + 1) ** 2 < 12)
                         or (part == 'head' and dx < 0 and dy < 1)):
        base = 'black'
    elif p=='tortie':
        patches=((-4,-2,4),(-1,1,2),(2,-2,2),(4,1,3)) if part=='body' else ((-3,-2,3),(1,0,2),(3,-4,3))
        if any((dx-x)**2+(dy-y)**2<r for x,y,r in patches):base='ginger'
    elif p=='point':
        if part in ('ear','tail','paw') or part=='head' and (dy<-4 or (dx-1)**2/15+dy**2/12<1):base='chocolate'
    elif p == 'bicolor':
        if part in ('ear', 'tail') or part == 'head' and abs(dx) > max(0, dy + 2):
            base = 'blue'
    elif p in ('bib', 'blaze', 'mask'):
        if part=='paw':base='white'
        if (part == 'body' and dx > 2 and dy > -1) or (part == 'head' and dy > 1):
            base = 'white'
        if part == 'head' and p in ('blaze', 'mask') and abs(dx) <= 1:
            base = 'white'
    elif p == 'saddle' and part == 'body' and dy < 1:
        base = 'black'
    elif p == 'tan' and part in ('paw', 'muzzle'):
        base = 'gold'
    if p == 'gradient' and dy > 0:
        base = 'white'
    return FUR['cat_ginger' if b.species=='cat' and base=='ginger' else base], 0


def fur_blob(s, b, cx, cy, rx, ry, part='body'):
    cx, cy, rx, ry = map(int, (cx, cy, rx, ry))
    mask = Sprite(W, H).ellipse(cx, cy, rx, ry, P.linen[3])
    return paint_fur(s,b,mask,cx,cy,rx,ry,part)


def paint_fur(s,b,mask,cx,cy,rx,ry,part='body'):
    for y,x in zip(*mask.px[:,:,3].nonzero()):
        x,y=int(x),int(y)
        ramp,shift=coat(b,part,x-cx,y-cy,rx,ry)
        edge=any(not (0<=xx<W and 0<=yy<H and mask.px[yy,xx,3])
                 for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
        shade=0 if edge else max(1,min(4,(3 if y<cy-1 and x<cx+2 else 1 if y>cy+ry//2 or x>cx+rx//2 else 2)+shift))
        s.set(x,y,ramp[shade])
    return s


def limb(s, b, x, y, length, dx=0, part='paw', view='side'):
    ramp, _ = coat(b, part, 0, 1, 1, 2)
    width=3 if b.species=='cat' else 5 if b.body>=7 else 4
    # A fleshy upper leg and a rounded paw, rather than two straight pixels.
    for i in range(abs(length)+1):
        yy=y+(i if length>=0 else -i)
        xx=x+round(dx*i/max(1,abs(length)))
        s.hline(xx,xx+width-1,yy,ramp[0])
        s.hline(xx+1,xx+width-2,yy,ramp[2])
        s.set(xx+1,yy,ramp[3])
    # Side sprites face right before mirroring: toes project FORWARD from the
    # ankle. Front/back paws are centred; rear views must not show toe clefts.
    py=y+length
    px=x+dx+1 if view=='side' else x+dx-1
    paw=width+1 if view=='side' else width+2
    s.hline(px+1,px+paw-2,py-2,ramp[0])
    s.hline(px,px+paw-1,py-1,ramp[0])
    s.hline(px+1,px+paw-2,py-1,ramp[3])
    s.hline(px+1,px+paw-2,py,ramp[1])
    if view=='side':s.set(px+paw-2,py-1,ramp[1])
    elif view=='front':
        s.set(px+2,py-1,ramp[1])
        if width>=4:s.set(px+paw-3,py-1,ramp[1])


def torso(s,b,cx,cy,rx,ry,hx,hy,head_y):
    """One connected body/neck mask; every head pose is rooted at its shoulder."""
    mask=Sprite(W,H).ellipse(cx,cy,rx,ry,P.linen[3])
    radius=2 if b.species=='cat' or b.body<7 else 3
    start=(cx+rx-2,cy-1);end=(hx-2,hy+head_y-radius)
    steps=max(abs(end[0]-start[0]),abs(end[1]-start[1]),1)
    for i in range(steps+1):
        x=round(start[0]+(end[0]-start[0])*i/steps)
        y=round(start[1]+(end[1]-start[1])*i/steps)
        mask.ellipse(x,y,radius,radius,P.linen[3])
    paint_fur(s,b,mask,cx,cy,rx,ry)


def cat_head(s,b,cx,cy,action,frame,front=False,back=False):
    """Soft cheeks and small bean eyes, inspired by the user's pixel-cat references."""
    mask=Sprite(W,H)
    spans=((-3,3),(-4,4),(-5,5),(-5,5),(-5,5),(-5,5),(-4,4),(-3,3),(-2,2))
    for j,(left,right) in enumerate(spans):mask.hline(cx+left,cx+right,cy-4+j,P.linen[3])
    # Two-pixel softened tips, broad outward roots: no isolated upright spikes.
    for side in (-1,1):
        for dy,left,right in ((-5,-5,-4),(-4,-5,-2),(-3,-5,-1)):
            if side>0:left,right=-right,-left
            mask.hline(cx+left,cx+right,cy+dy,P.linen[3])
    paint_fur(s,b,mask,cx,cy,5,4,'head')
    if back:return
    # Ear interiors remain inside the fur silhouette for every coat.
    for side in (-1,1):
        s.set(cx+side*4,cy-4,P.clay[3])
        s.hline(cx+side*4,cx+side*3,cy-3,P.blush[0])
    closed=action=='sleep' or action=='blink' and frame in (1,2) or action=='wake' and frame<2 or action=='drowsy' and frame in (2,3,4)
    contented=action in ('stretch','happy','nuzzle','content') and frame in (1,2,3,4)
    eyes=(cx-2,cx+2)
    eye_color=P.blue[3] if b.pattern in ('point','bicolor') else P.mustard[3] if b.color=='black' else P.ink[0]
    for x in eyes:
        if closed:s.hline(x-1,x,cy-1,P.ink[0])
        elif contented:
            s.set(x,cy-1,P.ink[0]).set(x-1,cy,P.ink[0]).set(x+1,cy,P.ink[0])
        else:
            if b.color=='black':s.set(x,cy,eye_color)
            else:s.vline(x,cy-1,cy,eye_color)
            if action=='surprised' and frame in (1,2,3):s.set(x,cy-2,eye_color)
    nose=cx if front else cx+1
    ramp,_=coat(b,'head',nose-cx,2,5,4)
    s.set(nose,cy+1,P.clay[3]).set(nose,cy+2,ramp[1])
    s.set(nose-1,cy+3,ramp[1]).set(nose+1,cy+3,ramp[1])
    s.set(cx-4,cy+1,ramp[1]).set(cx+4,cy+1,ramp[1])
    if action in ('drink','groom','happy') and frame%2:s.set(nose,cy+3,P.blush[0])


def tail(s, b, x, y, frame, action, front=False):
    ramp, _ = coat(b, 'tail', 0, 0, 2, 2)
    wag = (0, 1, 2, 1, -1, -2)[frame % 6] if action in ('happy','wag','play','idle','walk','run') else 0
    if b.species == 'cat':
        s.line(x,y,x-3,y-3+wag,ramp[0]).line(x-3,y-3+wag,x-3,y-6+wag,ramp[0])
        s.line(x+1,y,x-2,y-3+wag,ramp[2]).vline(x-2,y-5+wag,y-3+wag,ramp[3])
        if b.pattern in ('tabby','tortie'):
            for yy in (y-5+wag,y-2+wag):
                for xx,color in ((x-2,ramp[1]),(x-3,ramp[0])):
                    if s.inside(xx,yy) and s.px[yy,xx,3]:s.set(xx,yy,color)
    elif b.tail == 'stub':
        fur_blob(s,b,x-1,y-1+(wag%2),2,1,'tail')
    elif b.tail in ('curl','puff'):
        s.line(x,y,x-2,y-3+wag,ramp[0]).line(x+1,y,x-1,y-3+wag,ramp[2])
        fur_blob(s,b,x-2,y-3+wag,3 if b.tail=='curl' else 2,2,'tail')
        if b.tail=='curl':s.set(x-2,y-3+wag,ramp[1]).set(x-1,y-3+wag,ramp[1])
    else:
        s.line(x,y,x-4,y-3+wag,ramp[0]).line(x,y-1,x-4,y-4+wag,ramp[2])
        if b.tail in ('feather','fluffy'):
            s.line(x,y-2,x-4,y-5+wag,ramp[3]).line(x,y+1,x-3,y-2+wag,ramp[1])


def ear(s, b, x, y, side=0):
    ramp, _ = coat(b,'ear',0,0,2,2)
    if b.species=='cat' or b.ear in ('point','large'):
        height=4 if b.ear=='large' and b.species=='dog' else 3
        for row in range(height):
            s.hline(x-row//2,x+1+row//2,y+row,ramp[0])
            if row>0:s.set(x,y+row,P.clay[3] if b.species=='cat' else ramp[3])
    elif b.ear=='flop':
        fur_blob(s,b,x,y+4,2,4,'ear')
    elif b.ear=='round':
        fur_blob(s,b,x,y+2,2,2,'ear')
    else:
        s.rect(x-1,y+1,3,4,ramp[0]).rect(x,y+2,2,2,ramp[2])


def render(b, action='idle', frame=0, direction='right'):
    """Return a transparent, shadow-free sprite with a stable floor anchor."""
    if action not in actions(b.species) or direction not in DIRECTIONS:
        raise ValueError((b.id,action,direction))
    count=actions(b.species)[action][1];frame%=count
    t=frame/max(1,count-1);pulse=(0,0,1,0,0,0)[frame%6]
    cat=b.species=='cat';rx=6 if cat else b.body;ry=4 if cat else b.height
    leg=3 if cat else b.legs;head=5 if cat else b.head
    cx=13;cy=FEET-leg-ry+1;hx=22;hy=cy-4
    seated=action in ('sit','groom','scratch','knead','pant','bark','curious','content','drowsy','surprised')
    sit_amount=(t if action=='sit_down' else 1-t if action=='stand_up' else 1 if seated else 0)
    low=action in ('rest','sleep','eat','drink','sniff','stretch','nuzzle','roll')
    if action=='lie_down':low=t>.35
    if action=='wake':low=t<.65
    if sit_amount:
        cx+=2;cy+=round(sit_amount*2);rx-=round(sit_amount*2);hy-=round(sit_amount)
        cy=min(cy,FEET-ry)
    if low:
        cy=FEET-ry;hy=FEET-(4 if cat else head);leg=1
    if action in ('eat','drink','sniff'):hx+=1;hy=FEET-(4 if cat else head)-(frame%2)
    if action=='stretch':
        extend=(0,1,2,2,1,0)[frame%6]
        cx-=1;hx+=extend;hy=FEET-(4 if cat else head)-int(extend==0);cy-=1+int(extend>0)
    jump=0
    if action in ('run','pounce','play'):
        jump=(0,1,3,3,1,0)[frame%6];cy-=jump;hy-=jump
        if action=='pounce' and frame in (0,5):cy+=1;hy+=2
    if action=='idle':hy+=pulse
    if action in ('sit','rest') and frame==2:hy-=1
    if action=='sleep' and frame==2:ry+=1;cy-=1
    if action=='look':hx+=(0,0,1,1,0,-1)[frame%6]
    if action=='curious':hy+=(0,0,1,1,0,0)[frame%6]
    if action=='surprised':hy-=(0,1,1,1,0,0)[frame%6]
    if action=='shake':cx+=(-1,1,-1,1,0,0)[frame%6];hx+=(-1,1,-1,1,0,0)[frame%6]
    if action=='nuzzle':hx+=(-1,0,1,1,0,-1)[frame%6]
    if action=='sleep' or action=='wake' and t<.4:
        hx=19;hy=FEET-(4 if cat else head)
    s=Sprite(W,H)
    if direction in ('front','back'):
        return render_vertical(b,action,frame,direction,cy,hy,leg,jump,seated,low)
    if action=='roll':
        fur_blob(s,b,15,21,7,3)
        for x in (11,18):limb(s,b,x,20,-3-(frame%2),1)
        if cat:cat_head(s,b,24,21,action,frame)
        else:
            fur_blob(s,b,24,21,head,3,'head');s.hline(24,25,21,P.ink[0]);s.set(27,22,P.blush[0])
        tail(s,b,8,22,frame,action)
        return Sprite(W,H,px=s.px[:,::-1].copy()) if direction=='left' else s
    tail(s,b,max(6,cx-rx+1),cy,frame,action)
    stride=(0,1,2,0,-1,-2)[frame%6] if action in ('walk','run','pounce') else 0
    for x,shift in ((cx-rx+3,-stride),(cx+rx-2,stride)):
        limb(s,b,x-1,cy+ry-1,max(1,FEET-jump-(cy+ry-1)),shift)
    torso(s,b,cx,cy,rx,ry,hx,hy,4 if cat else head)
    if b.ear=='round' or b.id=='samoyed':
        for x in (cx-rx+2,cx+rx-2):fur_blob(s,b,x,cy-ry+1,2,2)
    if low:
        for x in (cx-rx+3,cx+rx-1):limb(s,b,x,FEET-1,0,2)
    elif sit_amount>.5:
        fur_blob(s,b,cx-2,FEET-3,3,3)
        limb(s,b,cx+rx-1,cy+1,FEET-cy-1)
    else:
        for x,shift in ((cx-rx+2,stride),(cx+rx-1,-stride)):
            limb(s,b,x,cy+ry-1,max(1,FEET-jump-(cy+ry-1)),shift)
    if cat:
        cat_head(s,b,hx,hy,action,frame)
    else:
        head_y=head
        ear(s,b,hx-2,hy-head_y-2)
        fur_blob(s,b,hx,hy,head,head_y,'head')
        ear(s,b,hx+1,hy-head_y-2)
        if b.ear=='round':fur_blob(s,b,hx-2,hy-head+1,2,2,'head')
        if b.ear=='flop':fur_blob(s,b,hx-3,hy,2,4,'ear')
        # Keep the approved canine head and muzzle proportions.
        muzzle=2 if b.ear=='round' else 3
        fur_blob(s,b,hx+3,hy+2,muzzle,2,'muzzle')
        eye_x=hx+1;closed=action=='sleep' or action=='blink' and frame in (1,2) or action=='wake' and t<.4 or action=='drowsy' and frame in (2,3,4) or action=='content' and frame in (2,3)
        if closed:s.hline(eye_x,eye_x+1,hy,P.ink[0])
        else:
            s.vline(eye_x,hy-1,hy,P.ink[0])
            s.set(eye_x,hy-1,P.ink[0])
            if action=='surprised' and frame in (1,2,3):s.set(eye_x,hy-2,P.ink[0])
        nose_x=hx+4 if b.ear=='round' else hx+5
        s.set(nose_x,hy+1,P.ink[0]).set(nose_x-1,hy+2,P.ink[0])
        if action in ('pant','bark','happy'):
            s.rect(hx+3,hy+3,2,1+(frame%2),P.ink[0]).set(hx+4,hy+4,P.blush[0])
        if action in ('drink','groom') and frame%2:
            s.set(nose_x-1,hy+3,P.blush[0])
    if action in ('groom','scratch'):
        px=hx-1 if action=='groom' else hx-5
        limb(s,b,px,hy+4 if action=='groom' else hy+3,-2-(frame%2),1)
        if action=='scratch':s.line(cx-2,FEET-2,px,hy+2,FUR[b.color][1])
    if action=='knead':
        for i,x in enumerate((cx+3,cx+6)):limb(s,b,x,FEET-3,2 if frame%2==i else 0,1)
    if action=='sleep':
        # Tail wraps across the paws, independently of the breathing head.
        ramp,_=coat(b,'tail',0,0,3,2)
        s.line(cx-rx+1,FEET-2,cx+4,FEET-1,ramp[0]).hline(cx-rx+2,cx+3,FEET-2,ramp[2])
    if direction=='left':return Sprite(W,H,px=s.px[:,::-1].copy())
    return s


def render_vertical(b,action,frame,direction,cy,hy,leg,jump,seated,low):
    cat=b.species=='cat';s=Sprite(W,H);cx=16
    head=5 if cat else b.head;rx=4 if cat else max(4,b.height+1)
    body_y=3 if cat else min(4,b.height)
    legs=3 if cat else b.legs
    cy=FEET-body_y if low else 21-body_y//2 if seated else FEET-legs-body_y
    hy=FEET-(4 if cat else head) if low else cy-3
    cy-=jump;hy=max((4 if cat else head)+3,hy-jump)
    if action in ('eat','drink','sniff'):hy=FEET-(4 if cat else head)-(frame%2)
    if action=='stretch':hy=FEET-(4 if cat else head)-(frame%2)
    if action in ('idle','wake','sit','rest','curious'):hy+=frame%2
    if action=='surprised' and frame in (1,2,3):hy-=1
    if action=='look':cx+=(-1,0,1,1,0,0)[frame%6]
    if action=='nuzzle':cx+=(-1,0,1,1,0,-1)[frame%6]
    if action=='shake':cx+=(-1,1,-1,1,0,0)[frame%6]
    hy=min(FEET-(4 if cat else head),hy)
    tail(s,b,16,cy-1,frame,action,True)
    stride=(0,1,0,-1,0,1)[frame%6] if action in ('walk','run','pounce') else 0
    spread=4 if cat or b.body<7 else 5
    for i,x in enumerate((cx-spread,cx+spread-2)):
        start=cy+body_y-1
        limb(s,b,x,start,max(0,FEET-jump-start)-max(0,stride if i else -stride),view=direction)
    if action in ('sleep','rest') and frame==2:body_y+=1;cy-=1
    fur_blob(s,b,cx,cy,rx,body_y)
    if action=='roll':
        for x in (cx-3,cx+2):limb(s,b,x,20,-4,0,view=direction)
    if cat:
        cat_head(s,b,cx,hy,action,frame,front=True,back=direction=='back')
        if action in ('groom','knead','scratch'):limb(s,b,cx-3,hy+4,-1-frame%2,1,view=direction)
        return s
    head_y=head
    ear(s,b,cx-head+1,hy-head_y-2)
    ear(s,b,cx+head-2,hy-head_y-2,1)
    fur_blob(s,b,cx,hy,head,head_y,'head')
    if b.ear in ('flop','round'):
        for x in (cx-head,cx+head):fur_blob(s,b,x,hy+1,2,3 if b.ear=='flop' else 2,'ear')
    if direction=='back':
        if action=='scratch':limb(s,b,cx+5,hy+3,-2-frame%2,view=direction)
        return s
    if not cat:fur_blob(s,b,cx,hy+2,3,2,'muzzle')
    closed=action=='sleep' or action=='blink' and frame in (1,2) or action=='drowsy' and frame in (2,3,4) or action=='content' and frame in (2,3)
    for x in (cx-2,cx+2):
        if closed:s.hline(x-1,x,hy,P.ink[0])
        else:
            s.vline(x,hy-1,hy,P.ink[0])
            if action=='surprised' and frame in (1,2,3):s.set(x,hy-2,P.ink[0])
    s.set(cx,hy+1,P.clay[3] if cat else P.ink[0])
    if cat:
        s.set(cx-1,hy+2,P.ink[0]).set(cx+1,hy+2,P.ink[0])
        s.set(cx-4,hy+2,P.oat[1]).set(cx+4,hy+2,P.oat[1])
    else:s.set(cx,hy+3,P.ink[0])
    if action in ('drink','pant','bark','groom') and frame%2:s.set(cx,hy+3,P.blush[0])
    if action in ('groom','knead','scratch'):
        limb(s,b,cx-3,hy+4,-1-frame%2,1,view=direction)
    return s
