// World-space position of the top of the actor's head (or an object's anchor).
// Map code decides when a quest can be picked up or continued.
function drawQuestMarker(ctx, x, headY, sign = "!") {
  const image = IMG.questMarker[sign];
  if (!image) return;
  const lift = reduceMotionUI ? 0 : Math.round(Math.sin(realClock * 3));
  ctx.drawImage(image, Math.round(x) - 4, Math.round(headY) - image.height - 3 + lift);
}
