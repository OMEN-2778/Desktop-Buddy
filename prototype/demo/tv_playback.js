// TV pictures stay emissive, but may never paint over foreground characters.
const homeActors=document.createElement('canvas');homeActors.width=W;homeActors.height=H;
const homeActorsCtx=homeActors.getContext('2d');homeActorsCtx.imageSmoothingEnabled=false;
const tvPicture=document.createElement('canvas');tvPicture.width=24;tvPicture.height=12;
const tvPictureCtx=tvPicture.getContext('2d');tvPictureCtx.imageSmoothingEnabled=false;
const tvPlayback={playing:false,clip:null,bag:[],next:0,start:0};
function nextTvFrame(){
  if(!tvPlayback.playing||realClock>=tvPlayback.next){
    if(!tvPlayback.bag.length){
      tvPlayback.bag=Object.keys(IMG.tv);
      for(let i=tvPlayback.bag.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[tvPlayback.bag[i],tvPlayback.bag[j]]=[tvPlayback.bag[j],tvPlayback.bag[i]];}
      const last=tvPlayback.bag.length-1;
      if(last>0&&tvPlayback.bag[last]===tvPlayback.clip)[tvPlayback.bag[0],tvPlayback.bag[last]]=[tvPlayback.bag[last],tvPlayback.bag[0]];
    }
    tvPlayback.clip=tvPlayback.bag.pop();tvPlayback.start=realClock;tvPlayback.next=realClock+8+Math.random()*6;tvPlayback.playing=true;
  }
  const frames=IMG.tv[tvPlayback.clip];
  return frames?.[reduceMotionUI?0:Math.floor((realClock-tvPlayback.start)*6)%frames.length]||null;
}
function drawTvPicture(ctx){
  const image=nextTvFrame();if(!image)return;
  const {x,y}=D.screens.tv;
  tvPictureCtx.clearRect(0,0,24,12);tvPictureCtx.globalCompositeOperation='source-over';tvPictureCtx.drawImage(image,0,0);
  // The exact alpha of the same foreground used by the house renderer, not a
  // rectangular cutout: hair gaps and transparent sprite edges stay correct.
  tvPictureCtx.globalCompositeOperation='destination-out';tvPictureCtx.drawImage(homeActors,-x,-y);
  tvPictureCtx.globalCompositeOperation='source-over';ctx.drawImage(tvPicture,x,y);
}
