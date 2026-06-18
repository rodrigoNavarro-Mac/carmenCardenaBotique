import base64
import hashlib
import hmac
import json
import os
import re
import time
from pathlib import PurePosixPath

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST


ALLOWED_BLOB_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_BLOB_IMAGE_SIZE = 8 * 1024 * 1024


def _base64(value):
    return base64.b64encode(value).decode("ascii")


def _safe_pathname(pathname):
    raw_name = PurePosixPath(pathname or "image").name
    filename = re.sub(r"[^A-Za-z0-9._-]+", "-", raw_name).strip(".-") or "image"
    if "." not in filename:
        filename = f"{filename}.jpg"
    return f"boutique/{filename}"


def _read_write_token():
    return os.getenv("BLOB_READ_WRITE_TOKEN") or os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")


def _store_id_from_token(token):
    parts = token.split("_")
    return parts[3] if len(parts) >= 4 else ""


def _client_token(token, pathname):
    store_id = _store_id_from_token(token)
    if not store_id:
        raise ValueError("Token de Vercel Blob invalido.")
    valid_until = int((time.time() + 15 * 60) * 1000)
    payload = {
        "pathname": pathname,
        "validUntil": valid_until,
        "allowedContentTypes": ALLOWED_BLOB_CONTENT_TYPES,
        "maximumSizeInBytes": MAX_BLOB_IMAGE_SIZE,
        "addRandomSuffix": True,
        "cacheControlMaxAge": 60 * 60 * 24 * 30,
    }
    encoded_payload = _base64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(token.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    signed_payload = _base64(f"{signature}.{encoded_payload}".encode("utf-8"))
    return f"vercel_blob_client_{store_id}_{signed_payload}"


@login_required
@require_POST
def vercel_blob_upload_token(request):
    token = _read_write_token()
    if not token:
        return JsonResponse({"error": "Falta configurar BLOB_READ_WRITE_TOKEN."}, status=503)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Solicitud invalida."}, status=400)

    if body.get("type") != "blob.generate-client-token":
        return JsonResponse({"error": "Tipo de evento invalido."}, status=400)

    payload = body.get("payload") or {}
    pathname = _safe_pathname(payload.get("pathname"))
    try:
        client_token = _client_token(token, pathname)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=503)
    return JsonResponse(
        {
            "type": "blob.generate-client-token",
            "clientToken": client_token,
        }
    )
