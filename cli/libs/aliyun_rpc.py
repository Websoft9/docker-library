from __future__ import annotations

import base64
import hashlib
import hmac
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

from libs import http


class AliyunApiError(RuntimeError):
    def __init__(
        self,
        action: str,
        code: object,
        message: str,
        status_code: int | None = None,
        label: str = "Aliyun",
    ) -> None:
        self.action = action
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"{label} {action} failed: {code} {message}".strip())


def percent_encode(value: object) -> str:
    return quote(str(value), safe="")


def sign(params: dict[str, str], access_key_secret: str) -> str:
    canonical = "&".join(
        f"{percent_encode(key)}={percent_encode(value)}" for key, value in sorted(params.items())
    )
    string_to_sign = "GET&%2F&" + percent_encode(canonical)
    digest = hmac.new(
        (access_key_secret + "&").encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def signed_params(
    action: str,
    params: dict[str, object],
    access_key_id: str,
    access_key_secret: str,
    version: str,
) -> dict[str, str]:
    merged: dict[str, str] = {
        "Format": "JSON",
        "Version": version,
        "AccessKeyId": access_key_id,
        "SignatureMethod": "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()),
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Action": action,
    }
    for key, value in params.items():
        if value is not None:
            merged[key] = str(value)
    merged["Signature"] = sign(merged, access_key_secret)
    return merged


def rpc_call(
    action: str,
    params: dict[str, object],
    access_key_id: str,
    access_key_secret: str,
    *,
    version: str,
    endpoint: str,
    label: str = "Aliyun",
) -> dict:
    response = http.get(
        endpoint,
        params=signed_params(action, params, access_key_id, access_key_secret, version),
    )
    try:
        payload = response.json()
    except ValueError as error:
        raise AliyunApiError(
            action,
            response.status_code,
            f"returned a non-JSON response (HTTP {response.status_code})",
            response.status_code,
            label,
        ) from error
    if not isinstance(payload, dict):
        raise AliyunApiError(
            action,
            response.status_code,
            "returned an unexpected payload",
            response.status_code,
            label,
        )
    if response.status_code >= 400 or payload.get("Code"):
        code = payload.get("Code") or response.status_code
        message = payload.get("Message") or response.reason
        raise AliyunApiError(action, code, message, response.status_code, label)
    return payload
