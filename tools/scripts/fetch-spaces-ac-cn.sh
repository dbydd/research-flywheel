#!/bin/bash
# Fetch a spaces.ac.cn URL through the mihomo proxy (the site is SNI-blocked on the direct path).
# Temporarily routes traffic through a working proxy node, then restores the user's settings.
# Usage: spaces_fetch.sh <outfile> <url> [referer]
S=/tmp/verge/verge-mihomo.sock
OUT="$1"; URL="$2"; REF="$3"
NODE="🇯🇵 日本-优化"
api(){ curl -sS --max-time 10 --unix-socket "$S" "$@"; }
PREV_MODE=$(api "http://localhost/configs" | python3 -c "import json,sys;print(json.load(sys.stdin).get('mode','rule'))")
PREV_NODE=$(api "http://localhost/proxies/GLOBAL" | python3 -c "import json,sys;print(json.load(sys.stdin).get('now',''))")
restore(){
  api -X PATCH -H 'Content-Type: application/json' -d "{\"mode\":\"$PREV_MODE\"}" -o /dev/null "http://localhost/configs"
  if [ -n "$PREV_NODE" ]; then
    api -X PUT -H 'Content-Type: application/json' -d "{\"name\":\"$PREV_NODE\"}" -o /dev/null "http://localhost/proxies/GLOBAL"
  fi
}
trap restore EXIT
api -X PUT -H 'Content-Type: application/json' -d "{\"name\":\"$NODE\"}" -o /dev/null "http://localhost/proxies/GLOBAL"
api -X PATCH -H 'Content-Type: application/json' -d '{"mode":"global"}' -o /dev/null "http://localhost/configs"
sleep 0.5
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
if [ -n "$REF" ]; then
  env no_proxy='*' NO_PROXY='*' http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= \
    curl -sS -L --max-time 60 --compressed -o "$OUT" -w "code=%{http_code} size=%{size_download} url=%{url_effective}\n" -A "$UA" -e "$REF" "$URL"
else
  env no_proxy='*' NO_PROXY='*' http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= \
    curl -sS -L --max-time 60 --compressed -o "$OUT" -w "code=%{http_code} size=%{size_download} url=%{url_effective}\n" -A "$UA" "$URL"
fi
