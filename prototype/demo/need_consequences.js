// Exhausted nonfatal needs leave condition moods, rather than renewing a timer
// every frame. Timed embarrassment is exactly 36 game hours for all personalities.
Object.assign(ML,{
 need_dirty_zero:{name:'恶心',emo:'uncomfortable',pts:5,until:'直到补充清洁',noCollapse:true,
  diary:['清洁彻底耗尽，身上的味道连自己都受不了。先洗一洗，再去和人打招呼。','袖口和头发都脏得不舒服，得认真清洁一下才能自在地出门。'],
  say:['不行，得先洗干净。','这味道连我自己都想躲。','先去洗澡，别硬撑着聊天。','干净一点再出门，自己也舒服。']},
 need_social_zero:{name:'难过 · 缺少陪伴',emo:'sad',pts:5,until:'直到补充社交',noCollapse:true,
  diary:['社交耗尽了，心里空了一块。想找个愿意听自己说话的人，哪怕只聊两句。','太久没好好交流，连打个招呼都开始犹豫了。想慢慢把和人的联系找回来。'],
  say:['想听听有人回应我的声音。','找个人聊两句吧，不用聊大事。','我是不是太久没联系大家了。','哪怕只说一句你好也好。']},
 need_fun_zero:{name:'难过 · 缺少乐趣',emo:'sad',pts:5,until:'直到补充娱乐',noCollapse:true,
  diary:['娱乐耗尽了，做什么都提不起劲。不是非得干大事，先找一点让自己开心的小乐趣。','一直没有给自己留轻松的时间，心情也闷了下来。该做点喜欢的事了。'],
  say:['想做点真的有意思的事。','好久没让自己轻松一下了。','看点喜欢的节目，慢慢缓一缓。','生活不能只剩下一直撑着。']}
});
Object.assign(ML.accident,{name:'难为情',pts:5,min:36*60,fixedDuration:true,noCollapse:true,
 diary:['没赶上厕所，清洁也彻底耗尽了。这份难为情得缓上三十六个游戏小时，先去洗干净再说。','还是没能憋住，衣服和身体都需要认真清洁。尴尬不会立刻消失，给自己三十六个游戏小时慢慢放下。'],
 say:['先洗干净，别的等会儿再说。','这件事我得缓好久……','谁也别提，我会慢慢恢复的。','已经发生了，先照顾好自己。']});
function usingToiletNow(){return mallToiletInside()||barToiletInside()||parkInsideToilet()||sim.mode==='act'&&sim.act==='toilet';}
function applyNeedConsequences(){
 const n=sim.needs;
 if(n.bladder<=0&&sim.mode!=='down'&&!usingToiletNow()){
  n.bladder=100;n.hygiene=0;addMood('accident');
  if(!asleep()){sim.queue=[];startAct('bath');}
 }
 for(const [id,key]of [['need_dirty_zero','hygiene'],['need_social_zero','social'],['need_fun_zero','fun']]){
  if(n[key]<=0){if(!moods.has(id))addMood(id,{words:!asleep()});}
  else if(moods.has(id))moods.delete(id);
 }
}
const DIRTY_NPC_REPLIES=[
 '那个……我们先隔远一点聊？你要不先洗个澡。',
 '不好意思，味道有点重，我先往那边走走。',
 '先别靠这么近，去洗一洗再打招呼吧。',
 '我鼻子今天比较灵……你先整理一下自己？',
 '不是不想认识你，就是现在得先透口气。',
 '你是不是该回去洗个澡了？我们下次再聊。',
 '先处理一下身上的味道吧，我在这儿有点待不住。',
 '话题先存着，你洗干净以后再来找我。',
 '嗯……我先去吹吹风，不好意思。',
 '咱们先暂停打招呼，清洁这件事比较着急。',
 '我往旁边站一点，你别误会，真是有点呛。',
 '先回去换洗一下吧，聊天下次还有机会。',
 '今天先不聊了，你也闻到那股味道了吧？',
 '这时候先别忙着交朋友，先和热水交个朋友。',
 '抱歉，我需要给鼻子一点空间。',
 '你先洗洗，回来再说，别勉强自己也别勉强我。',
 '我有点接不住这个味道……等你收拾好了再聊。',
 '先照顾好自己吧，这会儿我真没法站近聊天。',
 '我先让开一点。不是话题不好，是空气有点辛苦。',
 '今天这场聊天先改期，洗干净以后再碰面吧。'
];
let nextDirtyNpcReply=0;
function npcRefusesDirty(n,manual=false){
 if(sim.needs.hygiene>0||!n||(life.npcs||[]).indexOf(n)<0)return false;
 const due=manual?realClock>=(n.dirtyReplyAt??-Infinity)+3:realClock>=nextDirtyNpcReply;
 if(due){n.dirtyReplyAt=realClock;nextDirtyNpcReply=realClock+18;npcSay(n,pick(DIRTY_NPC_REPLIES));
  log(`${npcTalkName(n)}闻到身上的味道，委婉地回避了这次搭话。先补充清洁，再来认识彼此吧。`);}
 return true;
}
