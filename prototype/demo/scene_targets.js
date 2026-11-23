// Screen, source canvas and map coordinates share the same bottom-aligned projection.
function mapViewport(controller, height) {
  const {state, canvas} = controller;
  const camera = state.inside || state.mapOpen ? [0, 0] : [
    state.market ? Math.round(state.camX) : state.camera ?? state.camX ?? 0,
    state.camY || 0
  ];
  const top = height - canvas.height;
  return {
    top, height,
    point(event) {
      const bounds = view.getBoundingClientRect();
      const x = (event.clientX - bounds.left) * W / bounds.width;
      const y = (event.clientY - bounds.top) * height / bounds.height - top;
      return {x, y, worldX: x + camera[0], worldY: y + camera[1]};
    },
    scene(x, y) { return {x: x - camera[0], y: y - camera[1] + top}; },
    onCanvas(point) { return point.y >= 0 && point.y < canvas.height; },
  };
}

// The same one-pixel tolerance as furniture at home, after checking the actual
// opaque pixels of the objects in their drawing order.
function scenePixelHit(target, x, y, key = "inside") {
  const img = target.img;
  if (!img?.width || !img.height || img.complete === false) return false;
  const dx = Math.floor(x) - Math.round(target.x), dy = Math.floor(y) - Math.round(target.y);
  if (dx < -1 || dx > img.width || dy < -1 || dy > img.height) return false;
  if (!outlineCache.has(img)) outlineCache.set(img, outlineShape(img));
  return outlineCache.get(img)[key].has(dx + "," + dy);
}

function sceneTargetAt(targets, x, y) {
  for (const key of ["inside", "near"]) {
    for (let i = targets.length - 1; i >= 0; i--) {
      if (scenePixelHit(targets[i], x, y, key)) return targets[i];
    }
  }
  return null;
}

function sceneTargetsFor(entries) {
  return entries.map(([id, x, y, src]) => {
    const img = new Image();
    img.src = src;
    return {id, x, y, img};
  });
}


const flippedSceneSprites = new WeakMap();

function flippedSceneSprite(sprite) {
  let img = flippedSceneSprites.get(sprite);
  if (!img) {
    img = document.createElement("canvas");
    img.width = sprite.width;
    img.height = sprite.height;
    const ctx = img.getContext("2d");
    ctx.translate(img.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(sprite, 0, 0);
    flippedSceneSprites.set(sprite, img);
  }
  return img;
}

function sceneObjectId(images, x, y) {
  return sceneTargetAt(Object.entries(images).map(([id,img])=>({id,img,x:0,y:0})), x, y)?.id ?? null;
}
