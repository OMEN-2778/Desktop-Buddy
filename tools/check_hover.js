// node tools/check_hover.js [preview URL]
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require(process.env.PW||'playwright');
(async()=>{
  const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
  try {
    const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(process.argv[2]||'http://127.0.0.1:8773/');
    await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);
    await page.waitForTimeout(1300);
    const checked=await page.evaluate(()=>{
      closeGuide();speed=0;lifeFlags.cards={seen:[],last:1e9};
      const sprites=[...Object.entries(IMG.click),...Object.entries(IMG.out.bar.hover)];
      for(const [room,O]of Object.entries(IMG.out.mall.rooms))for(const [id,img]of Object.entries(O.hover))sprites.push([`${room}:${id}`,img]);
      for(const [zone,O]of Object.entries(IMG.out.park.zones))
        for(const [id,img]of Object.entries(O.hover))sprites.push([`${zone}:${id}`,img]);
      for(const it of MALL.items)sprites.push([`mall:${it.id}`,it.kind==='shop'?IMG.out.mall.hover[it.id]:IMG.out.mall.props[it.id]]);
      for(const [id,img]of sprites){
        if(!img)throw new Error('Missing interaction sprite: '+id);
        const w=img.width+2,h=img.height+2;
        const c=document.createElement('canvas');c.width=w;c.height=h;
        const ctx=c.getContext('2d');ctx.drawImage(img,1,1);
        const a=ctx.getImageData(0,0,w,h).data;
        const on=(x,y)=>x>=0&&y>=0&&x<w&&y<h&&a[(y*w+x)*4+3]>0;
        ctx.clearRect(0,0,w,h);drawObjectHover(ctx,img,1,1);
        const out=ctx.getImageData(0,0,w,h).data;
        let count=0;
        for(let y=0;y<h;y++)for(let x=0;x<w;x++){
          const expected=!on(x,y)&&(on(x-1,y)||on(x+1,y)||on(x,y-1)||on(x,y+1));
          const k=(y*w+x)*4;
          if((out[k+3]>0)!==expected)throw new Error(`${id}: contour mismatch at ${x},${y}`);
          if(expected){
            count++;
            if(![[255,196,64],[255,243,205]].some(rgb=>rgb.every((v,i)=>Math.abs(out[k+i]-v)<=1)))
              throw new Error(id+': inconsistent highlight palette');
          }
        }
        if(!count)throw new Error(id+': empty contour');
      }
      window.hoverScene=(place,id,zone='central')=>{
        sim.t=20*60;throughDoor(place);speed=0;sim.mode='idle';sim.act=null;sim.windup=null;sim.idleUntil=Infinity;
        sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
        if(place==='park'){sim.park={zone,seated:false,goal:null};arriveAt('park');}
        hoverId=id;glow=null;mallS.hover=null;render();
      };
      return sprites.length;
    });
    assert.ok(checked>=50);
    // Exercise the real renderers, not only the reusable outline function.
    const captures=[['bar','bar_seat:stool_0'],['bar','bar_counter'],['bar','bar_stage'],['bar','bar_wc'],
      ['park','park_bench','central'],['park','park_wc','lakeside'],['park','park_food','grove']];
    fs.mkdirSync('/workspace/artifacts/hover',{recursive:true});
    for(const [place,id,zone]of captures){
      const calls=await page.evaluate(({place,id,zone})=>{
        const original=drawObjectHover,seen=[];
        drawObjectHover=(ctx,img,x=0,y=0)=>{if(img)seen.push(img);original(ctx,img,x,y);};
        try{hoverScene(place,id,zone);}finally{drawObjectHover=original;}
        const expected=place==='bar'?IMG.out.bar.hover[id]:parkImages().hover[id];
        return seen.includes(expected);
      },{place,id,zone});
      assert.equal(calls,true,`${id}: renderer must use the shared contour`);
      await page.locator('#view').screenshot({path:`/workspace/artifacts/hover/${id.replace(':','-')}.png`});
    }
    // Scroll wrapping must highlight both visible copies of a stall at an edge.
    const copies=await page.evaluate(()=>{
      hoverScene('mall',null);const it=MALL.items.find(it=>it.kind!=='shop');mallS.hover=it;
      mallS.x=it.px+MALL.at+5;
      const original=drawObjectHover,seen=[];
      drawObjectHover=(ctx,img,x,y)=>{seen.push(x);original(ctx,img,x,y);};
      try{drawMallHover(bctx);}finally{drawObjectHover=original;}
      render();return [seen,MALL.nearW];
    });
    assert.deepEqual(copies[0],[copies[1]-5,-5],'Wrapped hover must follow the rendered stall, including its clipped copy');
    await page.locator('#view').screenshot({path:'/workspace/artifacts/hover/mall.png'});
    assert.equal(await page.evaluate(()=>{
      const it=MALL.items.find(it=>it.kind!=='shop');
      mallS.x=it.px+MALL.at-80;mallS.pointer=[80,90];render();
      const before=mallS.hover;
      mallS.x+=MALL.nearW/2;render();
      return before?.id===it.id && mallS.hover!==before;
    }),true,'Stationary pointer must reselect after the mall scrolls');
    await page.dispatchEvent('#view','pointerleave');
    assert.deepEqual(await page.evaluate(()=>[hoverId,mallS.hover]),[null,null]);
    // Check an actual pointer selection, then returning home clears it.
    await page.evaluate(()=>{hoverScene('park',null,'lakeside');});
    const at=await page.evaluate(()=>{const r=view.getBoundingClientRect();return[r.left+270*r.width/W,r.top+70*r.height/H];});
    await page.mouse.move(...at);
    assert.equal(await page.evaluate(()=>hoverId),'park_wc');
    await page.evaluate(()=>{throughDoor('home');render();});
    assert.equal(await page.evaluate(()=>hoverId),null);
    // A stale object from another scene cannot throw or leave an outline.
    await page.evaluate(()=>{hoverId='bar_counter';render();hoverId=null;});
    assert.deepEqual(errors,[]);
    console.log(`PASS: ${checked} alpha-derived contours and one palette; bar/park renderers; mall wrapping; real pointer; leave/scene cleanup; stale IDs`);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
