#!/usr/bin/env bash
cd /var/www/html/ai/apps/backend
set -uo pipefail

BASE="http://127.0.0.1:8000/api/v1"

# 0. health
echo "health: $(curl -s -m 3 $BASE/health | head -c 40)"

E="solo_$(date +%s)@test.com"; P="SoloPass123"
curl -s -o /tmp/r0.json -w "register HTTP:%{http_code}\n" -X POST "$BASE/auth/register" -H "Content-Type: application/json" -d "{\"email\":\"$E\",\"password\":\"$P\",\"roles\":[\"admin\"]}"
TOKEN=$(curl -s -X POST "$BASE/auth/login" -H "Content-Type: application/json" -d "{\"email\":\"$E\",\"password\":\"$P\"}" | .venv/bin/python3 -c "import sys,json;print(json.load(sys.stdin)['data']['access_token'])")
echo "token len: ${#TOKEN}"

echo "=== create integration WITHOUT base_url (simplified form: name+desc+method+api_key+code) ==="
curl -s -o /tmp/c5.json -w "create HTTP:%{http_code}\n" -X POST "$BASE/integrations" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"SoloAPI","description":"no base url needed","method":"POST","api_key":"sk-solo-42","enabled":true,"code":"curl -X POST https://api.example.com/v1/items -H \"Authorization: Bearer xyz\" \\ \n--data '\''{}'\''"}'
.venv/bin/python3 -c "
import json
x=json.load(open('/tmp/c5.json')).get('data') or {}
print('  id:',x.get('id'),'| name:',x.get('name'),'| method:',x.get('method'),'| enabled:',x.get('enabled'),'| has_code:',bool(x.get('code')),'| base_url:',x.get('base_url'))"
ID=$( .venv/bin/python3 -c "import json;print((json.load(open('/tmp/c5.json')).get('data') or {}).get('id',''))" )

echo "=== update: rotate key + change method (keep code+enabled) ==="
curl -s -o /tmp/u5.json -w "update HTTP:%{http_code}\n" -X PUT "$BASE/integrations/$ID" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"method":"PUT","api_key":"sk-solo-rotated-99"}'
.venv/bin/python3 -c "
import json
x=json.load(open('/tmp/u5.json')).get('data') or {}
print('  method:',x.get('method'),'| enabled:',x.get('enabled'),'| has_code:',bool(x.get('code')),'| fingerprint:',(x.get('key_fingerprint') or '')[:20])"

echo "=== non-admin denied create (no token) ==="
curl -s -o /dev/null -w "  unauth create HTTP:%{http_code} (401=ok)\n" -X POST "$BASE/integrations" -H "Content-Type: application/json" -d '{"name":"x"}'

echo "=== chat SSE stream frames ==="
CID=$(curl -s -X POST "$BASE/conversations" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"agent_kind":"chat"}' | .venv/bin/python3 -c "import sys,json;print(json.load(sys.stdin)['data']['id'])")
timeout 45 bash -c "curl -s -N -X POST '$BASE/conversations/$CID/messages/stream' -H 'Authorization: Bearer $TOKEN' -H 'Content-Type: application/json' -d '{\"content\":\"Reply with EXACTLY: SHIPPEDAC\",\"stream\":true}'" > /tmp/s7.txt
echo "  frames: $(grep -c '^data:' /tmp/s7.txt) (expect >=3)"
grep -oE '"type":"[a-z_]+"' /tmp/s7.txt | sort | uniq -c
grep -o "SHIPPEDAC" /tmp/s7.txt | head -1

echo "=== delete ==="
curl -s -o /dev/null -w "  delete HTTP:%{http_code}\n" -X DELETE "$BASE/integrations/$ID" -H "Authorization: Bearer $TOKEN"
echo DONE