// Desktop UI has one typography/spacing policy; world pixels may scale, text stays readable.
// Use the actual house width, never the surrounding browser viewport or nested multipliers.
const UI_SCALES=Object.freeze([25,50,75,100]);
function uiMetrics(width,height){
 const growth=Math.max(0,Math.min(1,(width-342)/1026)),font=(min,extra)=>Math.round(min+extra*growth);
 return {compact:width<520,contactCompact:width<420,contactColumns:width<300?2:3,stackedContacts:width<260,callStacked:width<300,
  needColumns:width<220?2:width<420?3:6,needHeight:width<220?300:width<420?210:150,
  caption:12,speech:font(17,3),label:font(12,1),body:font(13,3),control:font(12,2),heading:font(16,4),
  cardTitle:font(20,15),cardBody:font(13,9),name:font(12,4),pill:font(13,3),gap:width<520?4:8,padding:width<520?6:12};
}
function sizeGameUi(width,height){
 const m=uiMetrics(width,height),root=document.getElementById('widget'),style=root.style;root.dataset.uiSize=m.compact?'compact':'regular';
 for(const key of ['caption','label','body','control','heading','cardTitle','cardBody','name','pill','speech'])style.setProperty('--ui-font-'+key.replace(/[A-Z]/g,c=>'-'+c.toLowerCase()),m[key]+'px');
 style.setProperty('--needs-columns',m.needColumns);style.setProperty('--needs-panel-height',m.needHeight+'px');
 style.setProperty('--ui-gap',m.gap+'px');style.setProperty('--ui-padding',m.padding+'px');
 style.setProperty('--say-fs',m.speech+'px');
 style.setProperty('--ring-fs',m.control+'px');style.setProperty('--mp-fs',m.pill+'px');style.setProperty('--contact-name-fs',m.name+'px');
 return m;
}
