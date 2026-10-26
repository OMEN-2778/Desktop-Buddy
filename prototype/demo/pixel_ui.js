// Palette-only PNG nine-slices; every rounded corner is a staircase of pixels.
// Shared by pet surfaces, settings audio and the update toast.
const pixelUiStyle=document.createElement('style');
const pixelUiVars=theme=>Object.entries(D.pixelUi[theme]).map(([key,src])=>`--pixel-${key}:url("${src}");`).join('');
pixelUiStyle.textContent=`:root{${pixelUiVars('light')}}:root[data-theme="dark"]{${pixelUiVars('dark')}}@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){${pixelUiVars('dark')}}}`;
document.head.append(pixelUiStyle);
