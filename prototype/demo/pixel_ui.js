// Palette-only PNG nine-slices; every rounded corner is a staircase of pixels.
// Shared by pet surfaces, settings audio and the update toast.
const pixelUiStyle=document.createElement('style');
const pixelUiVars=theme=>Object.entries(D.pixelUi[theme]).map(([key,src])=>`--pixel-${key}:url("${src}");`).join('');
pixelUiStyle.textContent=`:root{${pixelUiVars('light')}}`;
document.head.append(pixelUiStyle);
