// The terminal with a live plane outside (owner, 2026-11-02): the parked plane is gone; now and
// then one slides left -> right out of the picture, either fast-to-slow (a landing roll, it
// touches down first) or slow-to-fast (a take-off, it lifts away). Layers: vista -> plane ->
// terminal front (mullions, sill, counter...). Integer pixels; no plane under reduced motion.
function createAirportPlanes(images){
 let fly=null,wait=1500+Math.random()*3000;
 const curve={land:t=>1-(1-t)**3,takeoff:t=>t**3};
 function launch(kind=Math.random()<.5?'land':'takeoff'){fly={kind,t:0,dur:kind==='land'?6500:7000};}
 function tick(dt){if(!fly){if((wait-=dt)<=0)launch();return;}if((fly.t+=dt)>=fly.dur){fly=null;wait=5000+Math.random()*9000;}}
 function where(){const p=fly.t/fly.dur,x=Math.round(-86+436*curve[fly.kind](p));
  const y=fly.kind==='land'?42-Math.round(Math.max(0,1-p/.28)**2*16):42-Math.round(Math.max(0,(p-.55)/.45)**2*20);return [x,y];}
 function draw(ctx,dt,still=false){
  if(still){ctx.drawImage(images.airport_terminal,0,0);return;}
  tick(dt);ctx.drawImage(images.airport_vista,0,0);
  if(fly){const [x,y]=where();ctx.drawImage(images.airport_plane,x,y);}
  ctx.drawImage(images.airport_terminal_front,0,0);
 }
 return {draw,launch,get flying(){return fly&&{kind:fly.kind,at:where()}}};
}
