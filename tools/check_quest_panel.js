// 任务 panel on the game-shell test page: diary hover reveals the button, hovering it opens the panel
// (unfinished quests first), leaving closes it. Usage: node tools/check_quest_panel.js [outDir]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/quest-panel',SCALE=+(process.argv[3]||50);fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});try{const p=await b.newPage({viewport:{width:1400,height:1000}}),errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.questBoard&&window.infeiQuests,null,{timeout:60000});
 await p.evaluate(s=>{closeGuide();prefs.guided=true;prefs.scale=s;fit();Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done'});const q=infeiQuests.Q();q.mill.step=9;q.letter.step=2;q.letter.day=0;q.stew={step:1,got:['carrot']};q.prints.step=1;},SCALE);
 const d=await p.locator('#diaryBox').boundingBox();await p.mouse.move(d.x+24,d.y+24,{steps:4});await p.waitForTimeout(600);
 assert(await p.evaluate(()=>document.getElementById('moodrow').classList.contains('quest-ready')&&!questBoard.isOpen));
 const t=await p.locator('#questTrigger').boundingBox();assert(t.x+t.width<=d.x+2,'button sits left of the diary');
 await p.mouse.move(t.x+24,t.y+24,{steps:6});await p.waitForTimeout(900);assert(await p.evaluate(()=>questBoard.isOpen));
 const v=await p.locator('#questPanel').boundingBox(),house=await p.locator('#view').boundingBox();await p.screenshot({path:path.join(out,'任务面板-'+SCALE+'.png'),clip:{x:t.x-6,y:v.y-6,width:v.x+v.width-t.x+12,height:v.height+12}});
 assert(v.y<=d.y&&Math.abs(v.y+v.height-house.y-house.height)<8,'panel spans diary top to house bottom');
 const rows=await p.evaluate(()=>[...document.querySelectorAll('.qb-card')].map(c=>[c.classList.contains('done'),c.querySelector('strong').textContent,c.querySelector('p').textContent]));console.log(rows);
 const firstDone=rows.findIndex(r=>r[0]);assert(firstDone>0&&rows.slice(firstDone).every(r=>r[0]),'unfinished first');
 await p.evaluate(()=>{infeiQuests.Q().letter.log=[{day:3,title:'念信',lines:[['阿婆','闺女，你认字吧？'],[nameOf(),'认得。'],['阿婆','帮我念念这个。'],{letter:'儿子的信 · 前年寄来',text:'妈：\n城里活多，今年先不回了。\n明年春天一定回来，带小雨一起。'},['阿婆','我就是想再听一遍。'],['>','我再给您念一遍']]}];questBoard.fill();});
 await p.locator('.qb-card',{hasText:'溪边的阿婆'}).click();await p.waitForTimeout(900);await p.screenshot({path:path.join(out,'任务回顾-'+SCALE+'.png'),clip:await p.locator('#questPanel').boundingBox()});
 assert.equal(await p.locator('.qb-letter').count(),1);await p.locator('.qb-back').click();await p.waitForTimeout(300);
 await p.mouse.move(1300,950,{steps:4});await p.waitForTimeout(900);assert(!(await p.evaluate(()=>questBoard.isOpen)));
 assert.deepEqual(errs,[]);console.log('PASS');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
