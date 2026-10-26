"""Append one full-size gossip set to each requested dialogue pool.
Source stories are hand-authored in prototype/demo/dialogue/*.txt. Existing
entries stay in order; this script is idempotent and never doubles metadata.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'prototype/demo'

def read(name):return json.loads((P/name).read_text())
def write(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def stories(name):
 rows=[line.split('|') for line in (P/'dialogue'/name).read_text().splitlines() if line.strip()]
 assert all(len(row)==4 for row in rows)
 assert len({row[0] for row in rows})==len(rows)
 return rows
BANK=stories('gossip_stories.txt');EARLY=stories('early_gossip.txt')
assert len(BANK)==630 and len(EARLY)==20
REPORT=[]

def row(index,early=False,invert=False,bed=False):
 title,a,b,c=(EARLY if early else BANK)[index]
 title=('初聊八卦·' if early else '枕边八卦·' if bed else '八卦·')+title
 # General social > means friend; friend-house > means hero.
 other=index%2==0
 lines=[('>' if other else '')+a,('' if other else '>')+b,('>' if other else '')+c]
 if invert:lines=[s[1:] if s.startswith('>') else '>'+s for s in lines]
 return [title,*lines]
def obj(r):return {'title':r[0],'lines':r[1:],'emo':'playful' if len(r[0])%3 else 'happy','moodName':'听到件趣事'}
def is_added(t):
 title=t[0] if isinstance(t,list) else t.get('title','')
 return title.startswith(('八卦·','初聊八卦·','枕边八卦·'))
def extend(target,addition,path):
 base=[r for r in target if not is_added(r)]
 assert len(base)==len(addition),(path,len(base),len(addition))
 target[:]=base+addition
 REPORT.append({'pool':path,'before':len(base),'added':len(addition),'after':len(target)})

def main():
 sd=read('social_dialogue.json');st=read('social_text.json');hv=read('home_visit_text.json');fv=read('friend_visit_text.json')
 for kind,start in [('call',50),('video',130)]:extend(sd['phone'][kind],[obj(row(i)) for i in range(start,start+50)],'phone.extra.'+kind)
 for j,level in enumerate(['familiar','friend','close','best']):
  extend(st['conversations'][level],[row(i) for i in range(340+j*16,356+j*16)],'relationship.base.'+level)
  extend(sd['relationship'][level],[row(i) for i in range(404+j*16,420+j*16)],'relationship.extra.'+level)
 for kind in ['text','call','video']:extend(sd['early'][kind],[obj(row(i,early=True)) for i in range(20)],'early.'+kind)
 extend(sd['visit']['common'],[row(i) for i in range(300)],'home.common')
 start=510
 for context,entries in sd['visit'].items():
  if context=='common':continue
  n=len([r for r in entries if not is_added(r)])
  extend(entries,[row(i) for i in range(start,start+n)],'home.'+context);start+=n
 assert start==630
 extend(st['visitTalks'],[row(i) for i in range(300,340)],'home.legacy')
 start=468
 for kind,stages in sd['everydayPersonality'].items():
  for stage,entries in enumerate(stages):
   n=len([r for r in entries if not is_added(r)])
   extend(entries,[obj(row(i)) for i in range(start,start+n)],f'personality.{kind}.{stage}');start+=n
 assert start==510
 extend(hv['bedTalks'],[row(i,bed=True) for i in range(200,280)],'sleepover.bed')
 extend(fv['early'],[row(i,early=True,invert=True) for i in range(12)],'friendHome.early')
 extend(fv['talks'],[row(i,invert=True) for i in range(50)],'friendHome.common')
 for name,value in [('social_dialogue.json',sd),('social_text.json',st),('home_visit_text.json',hv),('friend_visit_text.json',fv)]:write(name,value)
 channels={'callFriend':[obj(row(i)) for i in range(50)],'videoFriend':[obj(row(i)) for i in range(100,130)],'messages':[[row(i)[0],row(i)[1:]] for i in range(180,192)]}
 for key,base in [('callFriend',50),('videoFriend',30),('messages',12)]:REPORT.append({'pool':key,'before':base,'added':len(channels[key]),'after':base+len(channels[key])})
 write('dialogue/gossip_channels.json',channels)
 report={'newStoryTopics':650,'addedConversationEntries':sum(r['added'] for r in REPORT),'pools':REPORT,'scope':'friend messages, voice/video calls, relationship stages, personality conversations, home visits and sleepover chats; invitation/event narration/outdoor introductions unchanged'}
 assert report['addedConversationEntries']==1024
 write('dialogue/gossip_expansion_report.json',report)
 print('Added 1024 conversation entries across',len(REPORT),'pools; 630 gossip stories + 20 cautious first-contact stories')
if __name__=='__main__':main()
