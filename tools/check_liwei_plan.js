const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
 const p=await b.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 const root=require('node:path').resolve(__dirname,'../desktop/dist/autumn/new-town');
 await p.route('http://review.test/**',route=>{
   const file=new URL(route.request().url()).pathname.slice(1)||'index.html';
   return route.fulfill({path:require('node:path').join(root,file)});
 });
 await p.goto('http://review.test/');
 const result=await p.evaluate(()=>{
   const unreachable=Object.keys(layout.places).filter(name=>path(index(...at('airstrip')),index(...at(name)))===null);
   const roadCells=walk.reduce((a,b)=>a+b,0);
   const roots=[index(...at('airstrip'))], visited=new Set(roots);
   for(let n=0;n<roots.length;n++){
    const v=roots[n];for(const w of [v-cols,v+cols,v%cols?v-1:-1,v%cols<cols-1?v+1:-1])if(walk[w]&&!visited.has(w)){visited.add(w);roots.push(w)}
   }
   return {unreachable,roadCells,connected:visited.size,places:Object.keys(layout.places).length};
 });
 console.log(result);assert.deepEqual(result.unreachable,[]);assert.equal(result.roadCells,result.connected);
 await p.locator('button').click();const box=await p.locator('canvas').boundingBox();
 const click=async(x,y)=>p.mouse.click(box.x+x/994*box.width,box.y+y/2176*box.height);
 await click(505,692);await p.waitForFunction(()=>document.querySelector('output').textContent==='已到达');
 await click(770,2020);assert.match(await p.locator('output').innerText(),/无法落脚/);
 await click(598,2070);await p.waitForFunction(()=>document.querySelector('output').textContent==='已到达',null,{timeout:60000});
 assert.equal(await p.evaluate(()=>actors.slice(1).every(a=>a.stop>0)),true);assert.deepEqual(errors,[]);console.log('mouse, lake rejection, quay arrival, NPCs ok');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
