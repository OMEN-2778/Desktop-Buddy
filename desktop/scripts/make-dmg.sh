#!/bin/bash
# make-dmg.sh "<App Name>" <out.dmg>: the universal .app in a disk image with
# an Applications shortcut and a note on opening an unnotarized app. Plain
# hdiutil, no Finder scripting (that times out on CI runners).
set -euo pipefail
app="$1"; out="$2"
src="desktop/src-tauri/target/universal-apple-darwin/release/bundle/macos/${app}.app"
stage=$(mktemp -d)
cp -R "$src" "$stage/"
ln -s /Applications "$stage/应用程序"
cat > "$stage/第一次打不开请看这里.txt" <<NOTE
1. 把「${app}」拖进旁边的「应用程序」文件夹，再从「应用程序」里打开它。
   （不要直接在这个窗口里打开：那样存档和自动更新都可能出问题。）

2. 第一次打开时，如果提示「无法验证开发者」「Apple 无法检查其是否包含恶意软件」：
   打开「系统设置 → 隐私与安全性」，往下翻，找到「${app}」那一行，点「仍要打开」，
   再输入开机密码确认。以后就能正常打开了。

3. 如果提示「已损坏，无法打开」：打开「终端」，粘贴下面这行后按回车，再打开一次：
   xattr -cr "/Applications/${app}.app"

4. 它在屏幕顶部菜单栏右侧也有一个图标，可以显示 / 隐藏、置顶、退出。
NOTE
# the same steps as empty files, so they show right in the window (user)
for step in \
  "① 先把 ${app} 拖进「应用程序」，再从那里打开" \
  "② 弹出「无法打开」时，先点「好」" \
  "③ 打开 系统设置 → 隐私与安全性，往下翻到「安全性」" \
  "④ 点「仍要打开」，输入开机密码，再点「打开」" \
  "⑤ 或者：按住 Control 点图标，选「打开」" \
  "⑥ 还不行或提示「已损坏」，看「第一次打不开请看这里.txt」"; do
  : > "$stage/$step"
done
hdiutil create -volname "${app}" -srcfolder "$stage" -fs HFS+ -format UDZO -ov "$out"
rm -rf "$stage"
