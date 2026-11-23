let questMarkers = null;

// Record the actor's anchor in scene pixels after the camera transform.
// Paint the badges together once the scene, foreground, weather and lighting are ready.
function drawQuestMarker(ctx, x, headY, sign = "!") {
  const image = IMG.questMarker[sign];
  if (!questMarkers || !image) return;
  const transform = ctx.getTransform();
  const resolution = ctx.canvas.width / W;
  questMarkers.push({
    image,
    x: (x * transform.a + headY * transform.c + transform.e) / resolution,
    headY: (x * transform.b + headY * transform.d + transform.f) / resolution,
  });
}

function questMarkerArrowAreas(height) {
  if (parkNavigation.hidden) return [];
  const frame = view.getBoundingClientRect();
  return Array.from(parkNavigation.children).filter(button => !button.hidden).map(button => {
    const bounds = button.getBoundingClientRect();
    return {
      left: (bounds.left - frame.left) * W / frame.width,
      right: (bounds.right - frame.left) * W / frame.width,
      top: (bounds.top - frame.top) * height / frame.height,
      bottom: (bounds.bottom - frame.top) * height / frame.height,
    };
  });
}

function paintQuestMarkers() {
  if (!questMarkers.length || wiping || tripRun || cardHolds() || storyLocked() || pickOn || ringOf || sim.mode === "down") return;
  const scene = window.seasonMapTest?.ctl();
  if (scene?.state.door || scene?.state.mapOpen) return;
  const height = sceneHouseHeight();
  const offsetY = scene ? height - scene.canvas.height : 0;
  const arrows = questMarkerArrowAreas(height);
  const lift = reduceMotionUI ? 0 : Math.round(Math.sin(realClock * 3));
  vctx.save();
  vctx.scale(view.width / W, view.height / height);
  vctx.imageSmoothingEnabled = false;
  for (const {image, x, headY} of questMarkers) {
    const anchor = headY + offsetY;
    if (x < 0 || x >= W || anchor >= height) continue;
    const left = Math.max(1, Math.min(W - image.width - 1, Math.round(x) - Math.floor(image.width / 2)));
    if (anchor < image.height + 3) continue;   // no room for a whole badge above the visible head
    let top = Math.max(1, Math.round(anchor) - image.height - 3 + lift);
    for (const arrow of arrows) {
      if (left < arrow.right && left + image.width > arrow.left && top < arrow.bottom && top + image.height > arrow.top - 2) {
        top = Math.floor(arrow.top) - image.height - 2;
      }
    }
    if (top >= 1) vctx.drawImage(image, left, top);
  }
  vctx.restore();
}
