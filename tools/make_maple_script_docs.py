"""Rebuild the story-review copies of docs/story/MAPLE_FULL_SCRIPT.md:
prototype/story-review/full-script.html and maple-full-script.docx (every line its own
paragraph, speaker in bold, the protagonist's lines in blue, stage notes grey).
Usage: python3 tools/make_maple_script_docs.py"""
import html
import re
from pathlib import Path

import docx
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'docs/story/MAPLE_FULL_SCRIPT.md'
OUT = ROOT / 'prototype/story-review'
lines = SRC.read_text().split('\n')
SPEAKER = re.compile(r'^([^：（(\s]{1,12}?)(（电话）)?：(.*)$')
NOTE = ('触发', '提交', '演出', '接取', '提示', '确认提示', '取消', '共同核对点', '提交条件', '按钮', '出发前信息卡')

# ---- html
css = ('body{margin:0;background:#f4f1ea;color:#303b3a;font:17px/1.85 system-ui,sans-serif}main{max-width:900px;margin:auto;padding:24px}'
       'h1,h2,h3{line-height:1.5}h2{margin-top:48px;border-bottom:1px solid #ccd1c9}h3{margin-top:32px;color:#305e60}'
       'p{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0}a{color:#276b85}.n{color:#8a8f88;font-size:15px}.c{color:#a86a00;font-weight:600}'
       'b.me{color:#2a6ebb}nav{position:sticky;top:0;background:#f4f1ea;padding:12px;border-bottom:1px solid #ccd1c9;font-size:15px}')
out = [f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       f'<title>枫叶城完整剧情脚本</title><style>{css}</style><main><nav><a href="maple-full-script.docx">下载完整 Word</a> · '
       f'<a href="index.html">原版剧情梗概</a></nav>']
for raw in lines:
    t = raw.strip()
    if not t:
        continue
    e = html.escape(t)
    if t.startswith('### '):
        out.append(f'<h3>{html.escape(t[4:])}</h3>')
    elif t.startswith('## '):
        out.append(f'<h2>{html.escape(t[3:])}</h2>')
    elif t.startswith('# '):
        out.append(f'<h1>{html.escape(t[2:])}</h1>')
    elif t.startswith(NOTE) or t.startswith('（') or t.startswith('- '):
        out.append(f'<p class="n">{e}</p>')
    elif t.startswith(('选项', '最终选项', '汇合', '若', '路线', 'G1', 'G2', 'G3', 'H ', 'W ', 'R ', '诊所', '食堂', '机修间', '留下的人', '事务所', '再次交谈')):
        out.append(f'<p class="c">{e}</p>')
    else:
        m = SPEAKER.match(t)
        if m and not t.startswith('|'):
            who = m.group(1) + (m.group(2) or '')
            cls = ' class="me"' if m.group(1) == '我' else ''
            out.append(f'<p><b{cls}>{html.escape(who)}：</b>{html.escape(m.group(3))}</p>')
        else:
            out.append(f'<p>{e}</p>')
(OUT / 'full-script.html').write_text(''.join(out) + '</main></html>')

# ---- docx
d = docx.Document()
st = d.styles['Normal']
st.font.name = 'Microsoft YaHei'
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
for name in ('Heading 1', 'Heading 2', 'Heading 3', 'Title'):
    d.styles[name].font.name = 'Microsoft YaHei'
    d.styles[name].element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
for raw in lines:
    t = raw.strip()
    if not t:
        continue
    if t.startswith('### '):
        d.add_heading(t[4:], 2); continue
    if t.startswith('## '):
        d.add_heading(t[3:], 1); continue
    if t.startswith('# '):
        d.add_heading(t[2:], 0); continue
    p = d.add_paragraph()
    if t.startswith(NOTE) or t.startswith('（') or t.startswith('- '):
        r = p.add_run(t); r.italic = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        continue
    if t.startswith(('选项', '最终选项', '汇合', '若', '路线')):
        r = p.add_run(t); r.bold = True; r.font.color.rgb = RGBColor(0xb0, 0x6a, 0x00)
        continue
    m = SPEAKER.match(t)
    if m and not t.startswith('|'):
        r = p.add_run(m.group(1) + (m.group(2) or '') + '：'); r.bold = True
        if m.group(1) == '我':
            r.font.color.rgb = RGBColor(0x2a, 0x6e, 0xbb)
        p.add_run(m.group(3))
    else:
        p.add_run(t)
d.save(OUT / 'maple-full-script.docx')
print('ok')
