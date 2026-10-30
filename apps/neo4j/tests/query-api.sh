#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import base64
import json
import os
import urllib.request

credentials = f"{os.environ['W9_LOGIN_USER']}:{os.environ['W9_LOGIN_PASSWORD']}".encode()
request = urllib.request.Request(
    f"{os.environ['BASE_URL']}/db/neo4j/query/v2",
    data=json.dumps({"statement": "RETURN 1"}).encode(),
    headers={
        "Authorization": "Basic " + base64.b64encode(credentials).decode(),
        "Content-Type": "application/json",
    },
    method="POST",
)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


opener = urllib.request.build_opener(NoRedirect)
with opener.open(request, timeout=15) as response:
    payload = json.load(response)
    if response.status != 202 or payload.get("data", {}).get("values") != [[1]]:
        raise SystemExit("Neo4j Query API did not return the expected result")
PY
