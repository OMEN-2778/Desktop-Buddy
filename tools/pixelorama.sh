#!/usr/bin/env bash
# Workspace-local installation; no writes to the user's home or system packages.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pix_root="${PIXELORAMA_ROOT:-$(dirname "$repo_dir")/extra-tools}"
pix_app="$pix_root/Pixelorama-Linux-64bit/Pixelorama.x86_64"
pix_mcp="$pix_root/Pixelorama-MCP"
export XDG_DATA_HOME="$pix_root/xdg-data" XDG_CONFIG_HOME="$pix_root/xdg-config" XDG_CACHE_HOME="$pix_root/xdg-cache"
health() { python3 -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:7373/health",timeout=2).read().decode())'; }
case "${1:-health}" in
  setup)
    mkdir -p "$pix_root"
    python3 - "$pix_root" <<'PY'
import hashlib,sys,tarfile,urllib.request
from pathlib import Path
root=Path(sys.argv[1]);archive=root/'Pixelorama-Linux-64bit.tar.gz'
if not archive.exists():
    urllib.request.urlretrieve('https://github.com/Orama-Interactive/Pixelorama/releases/download/v1.2.3/Pixelorama-Linux-64bit.tar.gz',archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='e7bb3b5f485e3a67f06b15a2c8414a8a7c18b7c6d2cf73f6b3b5904d86821e4b', 'Pixelorama archive checksum changed'
if not (root/'Pixelorama-Linux-64bit/Pixelorama.x86_64').exists():
    with tarfile.open(archive) as t:t.extractall(root,filter='data')
PY
    if [ ! -d "$pix_mcp/.git" ]; then git clone --no-checkout https://github.com/abidoo22/Pixelorama-MCP.git "$pix_mcp"; fi
    git -C "$pix_mcp" fetch --depth 1 origin 56fd8aa94c0905591bd2515fe9823eb70d4496d2
    git -C "$pix_mcp" checkout --detach 56fd8aa94c0905591bd2515fe9823eb70d4496d2
    # Upstream's optional ESLint peers disagree; the drawing server uses SDK/Zod/TS.
    (cd "$pix_mcp/mcp-server" && npm ci --ignore-scripts --legacy-peer-deps --no-audit --no-fund --cache "$pix_root/npm-cache" && npm run build)
    ;;
  start)
    if health >/dev/null 2>&1; then exit 0; fi
    if [ ! -x "$pix_app" ] || [ ! -f "$pix_mcp/mcp-server/dist/index.js" ]; then echo 'Run bash tools/pixelorama.sh setup first.' >&2; exit 1; fi
    mkdir -p "$XDG_DATA_HOME/pixelorama/extensions"
    cp "$pix_mcp/pixelorama-plugin/PixMcpBridge.pck" "$XDG_DATA_HOME/pixelorama/extensions/"
    python3 - "$XDG_DATA_HOME/pixelorama/config.ini" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text() if p.exists() else ''
if re.search(r'^PixMcpBridge=',s,re.M):s=re.sub(r'^PixMcpBridge=.*$', 'PixMcpBridge=true',s,flags=re.M)
elif '[extensions]' in s:s=s.replace('[extensions]','[extensions]\nPixMcpBridge=true',1)
else:s+='\n[extensions]\nPixMcpBridge=true\n'
p.write_text(s)
PY
    nohup "$pix_app" --headless >"$pix_root/pixelorama.log" 2>&1 &
    python3 - <<'PY'
import time,urllib.request
for _ in range(40):
    try:
        with urllib.request.urlopen('http://127.0.0.1:7373/health',timeout=.3) as r:print(r.read().decode())
        break
    except OSError:time.sleep(.2)
else:raise SystemExit('Pixelorama bridge did not start; inspect extra-tools/pixelorama.log')
PY
    ;;
  mcp)
    bash "$repo_dir/tools/pixelorama.sh" start >&2
    exec node "$pix_mcp/mcp-server/dist/index.js"
    ;;
  health) health ;;
  *) echo 'Usage: bash tools/pixelorama.sh setup|start|health|mcp' >&2; exit 2 ;;
esac
