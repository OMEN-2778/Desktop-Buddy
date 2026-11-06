const {chromium}=require('playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file:///tmp/claude-0/promo/p2.html');await p.waitForTimeout(800);
const END=await p.evaluate(()=>PROMO.END);fs.writeFileSync('/tmp/claude-0/promo/snd.json',JSON.stringify(await p.evaluate(()=>PROMO.SND)));
fs.rmSync('/tmp/claude-0/promo/frames2',{recursive:true,force:true});fs.mkdirSync('/tmp/claude-0/promo/frames2');
const N=Math.round(END*30);for(let i=0;i<N;i++){await p.evaluate(t=>PROMO.render(t),i/30);await p.screenshot({path:`/tmp/claude-0/promo/frames2/${String(i).padStart(5,'0')}.jpg`,quality:92});if(i%150===0)console.log(i,N);}
console.log('done');await b.close();})();
