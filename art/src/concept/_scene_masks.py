"""Collect visible outlines as furnishings are painted into the room bitmap."""

import numpy as np
from pixelkit import Sprite


class SceneMasks:
    def __init__(self, scene, output):
        self.scene = scene
        self.output = output
        self.layers = []
        self.active = None

    def start(self, name=None):
        if self.output is None:
            return
        if self.active is not None:
            old_name, before = self.active
            self.layers.append((old_name, np.any(before != self.scene.px, axis=2)))
        self.active = (name, self.scene.px.copy()) if name else None

    def add(self, name, sprite, x, y):
        if self.output is None:
            return
        layer = Sprite(self.scene.w, self.scene.h).blit(sprite, x, y)
        self.layers.append((name, layer.px[..., 3] != 0))

    def finish(self):
        self.start()
        if self.output is None:
            return
        covered = np.zeros((self.scene.h, self.scene.w), dtype=bool)
        visible = []
        for name, pixels in reversed(self.layers):
            mask = pixels & ~covered
            covered |= pixels
            if not name or not mask.any():
                continue
            yy, xx = np.nonzero(mask)
            x, y = int(xx.min()), int(yy.min())
            crop = mask[y:yy.max()+1, x:xx.max()+1]
            outline = Sprite(crop.shape[1], crop.shape[0])
            outline.px[..., 3] = crop * 255
            visible.append((name, x, y, outline))
        self.output.extend(reversed(visible))
