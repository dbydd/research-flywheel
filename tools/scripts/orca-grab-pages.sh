#!/bin/bash
# Grab several spaces.ac.cn pages through the Orca browser into /tmp.
# Usage: sp_batch.sh <name=url> ...
set -e
for pair in "$@"; do
  name="${pair%%=*}"; url="${pair#*=}"
  out="/tmp/sp_${name}.html"
  tmp=$(mktemp /tmp/spb.XXXXXX)
  orca goto --url "$url" --json > /dev/null
  sleep 2
  orca eval --expression "document.documentElement.outerHTML" --json > "$tmp"
  python3 - "$tmp" "$out" "$name" <<'PY'
import json,sys,re
tmp,out,name=sys.argv[1],sys.argv[2],sys.argv[3]
d=json.load(open(tmp))
h=d['result']['result']
open(out,'w').write(h)
k3=h.count('K3')
print(f"{name}: bytes={len(h)} K3_hits={k3}")
PY
  rm -f "$tmp"
done
