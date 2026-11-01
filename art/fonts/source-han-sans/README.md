# Autumn signs · 思源黑体

Source: Adobe Source Han Sans SC Medium, release branch.
https://github.com/adobe-fonts/source-han-sans/blob/release/OTF/SimplifiedChinese/SourceHanSansSC-Medium.otf

SIL Open Font License 1.1, included as LICENSE.txt. Subset using fontTools to the
Chinese characters used by autumn artwork; renamed Buddy Autumn Signs for this
derivative. Original glyph outlines unchanged. OTF supports art authoring; WOFF
is embedded in the test game / art inspector, with no remote font request.
Only sign lettering uses smooth font rendering per owner's explicit exception;
all scenery remains native pixel artwork. When adding sign text, regenerate the
subset from upstream with the union of existing and new characters.

Regenerate: `python tools/subset_autumn_font.py /path/to/SourceHanSansSC-Medium.otf`

Upstream OTF SHA-256: `1df61d31687d04fd2f928a3bb6ca6cd61f0e988cc267cf317f32406edbb49f70`
