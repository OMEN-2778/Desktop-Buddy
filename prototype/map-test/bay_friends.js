// 草帽湾认识的人进人脉（owner 2026-11-06：“在草帽湾遇到的人，回主世界还能不能约出来玩？”）。
// The first time one of the bay's main people talks with her, they swap numbers exactly the way she meets someone
// out in the main world (meetWorldNpc: 面熟 at 8, a diary line, the 第一次认识 memory, personality hints). From then
// on they are ordinary contacts: calls, messages, video, visits to her house and outings all come from the main
// world's social system. Talking with them again on the island counts as meeting them (as it does out in town).
(function(){
 const L=summerLife,inBay=()=>sim.place==='summer_test';
 // same looks as on the island (summer_life.js / summer_more.js build them from these seeds)
 const BAY=[
  {id:'bay_alo',name:'阿洛',speaker:['阿洛'],g:'m',seed:301,personality:{social:72,care:45,sensitivity:-15}},
  {id:'bay_lei',name:'蕾拉妮',speaker:['蕾拉妮'],g:'f',seed:433,personality:{social:25,care:62,sensitivity:58}},
  {id:'bay_kai',name:'卡伊诺',speaker:['卡伊诺'],g:'m',seed:577,personality:{social:-42,care:35,sensitivity:52}},
  {id:'bay_mia',name:'米娅',speaker:['咖啡店的米娅','米娅'],g:'f',seed:919,personality:{social:55,care:48,sensitivity:5}},
  {id:'bay_hai',name:'阿海',speaker:['救生员阿海','阿海'],g:'m',seed:1409,personality:{social:30,care:66,sensitivity:-30}},
  {id:'bay_mai',name:'小麦',speaker:['冲浪教练小麦','小麦'],g:'f',seed:1511,personality:{social:64,care:12,sensitivity:-22}},
  {id:'bay_noa',name:'诺亚',speaker:['潜水教练诺亚','诺亚'],g:'m',seed:1613,personality:{social:-12,care:52,sensitivity:24}}];
 const who=new Map();for(const b of BAY)for(const s of b.speaker)who.set(s,b);
 const seenToday=new Map();
 function meet(b){
  if(!socialState.contacts.some(c=>c.id===b.id)&&!socialState.world.some(c=>c.id===b.id)){
   const look=doll.normalize({...L.person(b.name,b.g,b.seed).look});
   socialState.world.push({id:b.id,name:b.name,look,child:false,personality:{...b.personality}});   // only for this meeting:
   try{meetWorldNpc({personId:b.id});}finally{socialState.world=socialState.world.filter(c=>c.id!==b.id);}   // they never turn up as strangers elsewhere
   seenToday.set(b.id,Math.floor(sim.t/1440));showHint(`和${b.name}交换了联系方式，回家后也能联系`);return;}
  if(seenToday.get(b.id)===Math.floor(sim.t/1440))return;   // seeing them again: once a day, as out in town
  seenToday.set(b.id,Math.floor(sim.t/1440));
  const c=socialState.contacts.find(c=>c.id===b.id);if(c){c.lastSeen=sim.t;c.forgotten=false;finishContactTalk(c.id,'meet');contactsSig='';}
 }
 const sp=springFarm.speech,oShow=sp.show;
 sp.show=function(speaker,words,o){if(inBay()){const b=who.get(speaker);if(b)try{meet(b);}catch(e){console.warn('bay friend',e);}}return oShow.apply(this,arguments);};
 window.bayFriends={BAY,meet};
})();
