// The playable surface is the union of the same road rectangles used by the artwork.
function autumnTownNavigation({width,height}, {streets,obstacles}) {
    const cell = 4, half = cell / 2;
    const cols = Math.ceil(width / cell), rows = Math.ceil(height / cell);
    const floor = new Uint8Array(cols * rows);
    for (const [left,top,right,bottom] of streets) {
        for (let y=Math.ceil((top*2-half)/cell); y*cell+half<=bottom*2; y++) {
            for (let x=Math.ceil((left*2-half)/cell); x*cell+half<=right*2; x++) floor[y*cols+x]=1;
        }
    }
    for (const [left,top,right,bottom] of obstacles) {
        for (let y=Math.floor(top/cell); y<=Math.floor(bottom/cell); y++) {
            for (let x=Math.floor(left/cell); x<=Math.floor(right/cell); x++) floor[y*cols+x]=0;
        }
    }
    const point = index => ({x:index%cols*cell+half,y:Math.floor(index/cols)*cell+half});
    function nearest(x,y) {
        const col = Math.max(0,Math.min(cols-1,Math.floor(x/cell)));
        const row = Math.max(0,Math.min(rows-1,Math.floor(y/cell)));
        let best = null;
        for (let radius=0; radius<Math.max(cols,rows); radius++) {
            const left=Math.max(0,col-radius), right=Math.min(cols-1,col+radius);
            const top=Math.max(0,row-radius), bottom=Math.min(rows-1,row+radius);
            for (let j=top; j<=bottom; j++) {
                for (let k=left; k<=right; k++) {
                    if (Math.max(Math.abs(k-col),Math.abs(j-row))!==radius) continue;
                    const index=j*cols+k;
                    if (!floor[index]) continue;
                    const p=point(index), d=Math.hypot(p.x-x,p.y-y);
                    if (!best || d<best.d) best={...p,d,index};
                }
            }
            if (best && radius*cell>=best.d) return best;
        }
        return best;
    }
    const previous = new Int32Array(floor.length), queue = new Int32Array(floor.length);
    let searchStart = -1, head = 0, tail = 0;
    function route(from,x,y) {
        const first=nearest(from.x,from.y), last=nearest(x,y);
        if (!first || !last) return [];
        if (searchStart!==first.index) {
            searchStart=first.index;
            previous.fill(-1);
            previous[first.index]=first.index;
            queue[0]=first.index;
            head=0;tail=1;
        }
        function add(next,here) {
            if (!floor[next] || previous[next]!==-1) return;
            previous[next]=here;queue[tail++]=next;
        }
        // Leave the frontier ready for another destination from the same cell.
        while (head<tail && previous[last.index]===-1) {
            const here=queue[head++];
            add(here-cols,here);
            if (here%cols) add(here-1,here);
            if (here%cols<cols-1) add(here+1,here);
            add(here+cols,here);
        }
        if (previous[last.index]===-1) return [];
        const bends=[];
        let index=last.index, direction=0;
        while (index!==first.index) {
            const parent=previous[index], step=index-parent;
            if (step!==direction) bends.unshift({...point(index),kind:"street"});
            direction=step;index=parent;
        }
        // A new click can interrupt a move midway along a segment.
        if (first.d>.01) bends.unshift({x:first.x,y:first.y,kind:"street"});
        if (first.x!==from.x && first.y!==from.y) bends.unshift({x:first.x,y:from.y,kind:"street"});
        return bends;
    }
    function step(from,dx,dy) {
        const spot=nearest(from.x,from.y);
        if (spot.d>.05 && dx*(spot.x-from.x)+dy*(spot.y-from.y)>0) return spot;
        for (const [a,b] of [[dx,0],[0,dy]]) {
            if (!a&&!b) continue;
            const x=spot.x+a*cell,y=spot.y+b*cell;
            if (x<0||x>=width||y<0||y>=height) continue;
            if (floor[spot.index+a+b*cols]) return {x,y};
        }
        return null;
    }
    function nearby(from) {
        const points=[];
        for(let dy=-96;dy<=96;dy+=16) for(let dx=-96;dx<=96;dx+=16) {
            if (dx*dx+dy*dy<625) continue;
            const x=Math.floor((from.x+dx)/cell),y=Math.floor((from.y+dy)/cell);
            if (x<0||x>=cols||y<0||y>=rows||!floor[y*cols+x]) continue;
            points.push(point(y*cols+x));
        }
        return points;
    }
    return {nearest,route,step,nearby};
}
