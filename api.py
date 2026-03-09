#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Broker Application API for profile submissions.
"""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
BROKER_ALLOWED_PROFILE_DOMAINS = (
    "linkedin.com",
    "instagram.com",
    "facebook.com",
    "fb.com",
)
BROKER_ALLOWED_STORE_SLUGS = {
    "diplan",
    "zentrix",
    "zentrix-prime",
    "as-sure",
    "bliss",
    "alleman",
    "affinity",
    "serra",
    "valorize",
}


def _runtime_environment():
    """Infer runtime environment for analytics/debug responses."""
    vercel_env = (os.environ.get("VERCEL_ENV") or "").strip().lower()
    if vercel_env == "production":
        return "production"
    if vercel_env == "preview":
        return "preview"
    if vercel_env == "development":
        return "local"

    flask_env = (os.environ.get("FLASK_ENV") or "").strip().lower()
    if flask_env == "production":
        return "production"

    return "local"


def _safe_json_loads(raw_value):
    """Parse JSON without raising and only return objects."""
    if not raw_value:
        return {}

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return {}

    return parsed if isinstance(parsed, dict) else {}


def _clean_utm_payload(raw_utm):
    """Return only supported attribution keys as trimmed strings."""
    if not isinstance(raw_utm, dict):
        return {}

    cleaned = {}
    for key in ("source", "medium", "campaign", "content", "term"):
        value = raw_utm.get(key)
        if value is None:
            continue

        value = str(value).strip()
        if value:
            cleaned[key] = value

    return cleaned


def _normalize_profile_url(raw_value):
    """Validate and normalize profile URLs accepted by the landing."""
    value = (raw_value or "").strip()
    if not value:
        return None, "profile_url_required"

    if not value.startswith(("http://", "https://")):
        value = f"https://{value}"

    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None, "invalid_profile_url"

    hostname = (parts.hostname or "").lower()
    is_allowed = any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in BROKER_ALLOWED_PROFILE_DOMAINS
    )
    if not is_allowed:
        return None, "invalid_profile_domain"

    normalized = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))
    return normalized, None


def _infer_profile_type(profile_url):
    """Infer profile type from the normalized profile URL."""
    if not profile_url:
        return ""

    hostname = (urlsplit(profile_url).hostname or "").lower()
    if hostname == "linkedin.com" or hostname.endswith(".linkedin.com"):
        return "linkedin"
    if hostname == "instagram.com" or hostname.endswith(".instagram.com"):
        return "instagram"
    if (
        hostname == "facebook.com"
        or hostname.endswith(".facebook.com")
        or hostname == "fb.com"
        or hostname.endswith(".fb.com")
    ):
        return "facebook"

    return "other"


def _load_broker_destination_urls():
    """Load one or many destination URLs for broker applications."""
    raw_values = [
        os.environ.get("BROKER_APPLICATIONS_DESTINATION_URLS", ""),
        os.environ.get("BROKER_APPLICATIONS_TARGET_URL", ""),
    ]
    urls = []
    for raw_value in raw_values:
        for item in raw_value.split(","):
            url = item.strip()
            if url and url not in urls:
                urls.append(url)

    return urls


def _allow_unconfigured_broker_destination():
    """Allow local-style acceptance without destinations when explicitly enabled."""
    raw_value = (os.environ.get("BROKER_APPLICATIONS_ALLOW_UNCONFIGURED") or "").strip().lower()
    return raw_value in {"1", "true", "yes", "on"}


def _broker_timeout_seconds():
    """Return the upstream timeout in seconds."""
    try:
        timeout_ms = int(os.environ.get("BROKER_APPLICATIONS_TIMEOUT_MS", "10000"))
    except ValueError:
        timeout_ms = 10000

    return max(timeout_ms, 1000) / 1000.0


def _forward_broker_application(url, payload):
    """Forward an application payload to a configured downstream endpoint."""
    request_body = json.dumps(payload).encode("utf-8")
    request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "ClickLeadsLanding/1.0",
    }
    downstream_request = urllib.request.Request(
        url=url,
        data=request_body,
        headers=request_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            downstream_request,
            timeout=_broker_timeout_seconds(),
        ) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
            body = _safe_json_loads(raw_body)
            status_code = response.getcode()
            success = 200 <= status_code < 300 and body.get("success", True) is not False
            return {
                "url": url,
                "status": status_code,
                "success": success,
                "body": body,
                "error": "" if success else body.get("error") or f"HTTP {status_code}",
            }
    except urllib.error.HTTPError as exc:
        raw_body = exc.read().decode("utf-8", errors="replace")
        body = _safe_json_loads(raw_body)
        return {
            "url": url,
            "status": exc.code,
            "success": False,
            "body": body,
            "error": body.get("error") or f"HTTP {exc.code}",
        }
    except Exception as exc:
        return {
            "url": url,
            "status": None,
            "success": False,
            "body": {},
            "error": str(exc),
        }


def _json_error(status_code, request_id, message, error_type, **extra):
    """Build a consistent error response payload."""
    payload = {
        "success": False,
        "request_id": request_id,
        "error": message,
        "error_type": error_type,
        "environment": _runtime_environment(),
    }
    payload.update({key: value for key, value in extra.items() if value not in (None, "")})
    return jsonify(payload), status_code


@app.route("/api/broker-applications", methods=["POST"])
def broker_applications():
    """
    Receive profile submissions and confirm success only after backend handling.

    Success rule:
    - With configured downstream destinations: every configured destination must
      return a successful response (2xx and success != false).
    - Without downstream destinations: only local/preview environments accept the
      payload and log it locally for test validation. Production returns 503.
    """
    request_id = uuid4().hex

    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return _json_error(
                400,
                request_id,
                "Invalid JSON payload.",
                "validation_error",
                destination_channel="invalid_payload",
            )

        store_slug = (data.get("store_slug") or data.get("storeSlug") or "").strip()
        store_name = (data.get("store_name") or data.get("storeName") or "").strip()
        profile_url_raw = data.get("profile_url") or data.get("profileUrl") or ""

        if not store_slug:
            return _json_error(
                400,
                request_id,
                "store_slug is required.",
                "validation_error",
                destination_channel="validation_error",
            )

        if store_slug not in BROKER_ALLOWED_STORE_SLUGS:
            return _json_error(
                400,
                request_id,
                "Store slug is not allowed.",
                "validation_error",
                destination_channel="validation_error",
            )

        if not store_name:
            return _json_error(
                400,
                request_id,
                "store_name is required.",
                "validation_error",
                destination_channel="validation_error",
            )

        normalized_profile_url, profile_error = _normalize_profile_url(profile_url_raw)
        if profile_error:
            return _json_error(
                400,
                request_id,
                profile_error,
                "validation_error",
                destination_channel="validation_error",
            )

        normalized_payload = {
            "event_type": (data.get("event_type") or "broker_application"),
            "store_slug": store_slug,
            "store_name": store_name,
            "profile_url": normalized_profile_url,
            "submitted_at": (
                data.get("submitted_at")
                or data.get("submittedAt")
                or datetime.now(timezone.utc).isoformat()
            ),
            "page": (data.get("page") or "").strip(),
            "tenantSlug": (data.get("tenantSlug") or data.get("tenant") or "default").strip(),
            "utm": _clean_utm_payload(data.get("utm")),
            "pageUrl": (data.get("pageUrl") or data.get("page_url") or "").strip(),
            "environment": _runtime_environment(),
            "profile_type": _infer_profile_type(normalized_profile_url),
        }

        destination_urls = _load_broker_destination_urls()
        if destination_urls:
            downstream_results = [
                _forward_broker_application(url, normalized_payload)
                for url in destination_urls
            ]
            all_succeeded = all(result["success"] for result in downstream_results)
            if not all_succeeded:
                first_error = next(
                    (result["error"] for result in downstream_results if not result["success"]),
                    "Destination request failed.",
                )
                app.logger.error(
                    "[BROKER_APPLICATION_FORWARD_FAILED] request_id=%s results=%s",
                    request_id,
                    json.dumps(downstream_results, ensure_ascii=True),
                )
                return _json_error(
                    502,
                    request_id,
                    first_error,
                    "destination_error",
                    destination_channel="webhook_proxy",
                    profile_type=normalized_payload["profile_type"],
                )

            merged_context = {}
            for key in ("filialSlug", "supervisor", "city", "state", "destination_channel"):
                value = next(
                    (
                        result["body"].get(key)
                        for result in downstream_results
                        if isinstance(result.get("body"), dict) and result["body"].get(key)
                    ),
                    "",
                )
                if value:
                    merged_context[key] = value

            user_message = next(
                (
                    result["body"].get("user_message") or result["body"].get("message")
                    for result in downstream_results
                    if isinstance(result.get("body"), dict)
                    and (
                        result["body"].get("user_message")
                        or result["body"].get("message")
                    )
                ),
                "Perfil enviado. O supervisor da loja sera notificado.",
            )
            destination_channel = merged_context.get("destination_channel") or "webhook_proxy"
            app.logger.info(
                "[BROKER_APPLICATION_FORWARD_SUCCESS] request_id=%s store=%s destinations=%s",
                request_id,
                store_slug,
                len(destination_urls),
            )

            response_payload = {
                "success": True,
                "request_id": request_id,
                "user_message": user_message,
                "destination_channel": destination_channel,
                "environment": normalized_payload["environment"],
                "profile_type": normalized_payload["profile_type"],
                "tenant": normalized_payload["tenantSlug"],
                "loja": normalized_payload["store_name"],
                "success_rule": "all_configured_destinations_succeeded",
            }
            response_payload.update({
                key: value
                for key, value in merged_context.items()
                if key != "destination_channel"
            })
            return jsonify(response_payload), 200

        if normalized_payload["environment"] == "production" and not _allow_unconfigured_broker_destination():
            app.logger.error(
                "[BROKER_APPLICATION_UNCONFIGURED] request_id=%s store=%s",
                request_id,
                store_slug,
            )
            return _json_error(
                503,
                request_id,
                "Supervisor destination is not configured.",
                "configuration_error",
                destination_channel="unconfigured",
                profile_type=normalized_payload["profile_type"],
            )

        if normalized_payload["environment"] == "production":
            app.logger.warning(
                "[BROKER_APPLICATION_UNCONFIGURED_BYPASS] request_id=%s store=%s",
                request_id,
                store_slug,
            )

        app.logger.info(
            "[BROKER_APPLICATION_LOCAL_ACCEPTED] request_id=%s payload=%s",
            request_id,
            json.dumps(normalized_payload, ensure_ascii=True),
        )
        return jsonify({
            "success": True,
            "request_id": request_id,
            "user_message": "Perfil recebido no backend local para teste.",
            "destination_channel": "local_log",
            "environment": normalized_payload["environment"],
            "profile_type": normalized_payload["profile_type"],
            "tenant": normalized_payload["tenantSlug"],
            "loja": normalized_payload["store_name"],
            "success_rule": "validated_and_logged_locally",
        }), 200
    except Exception as exc:
        app.logger.exception(
            "[BROKER_APPLICATION_EXCEPTION] request_id=%s error=%s",
            request_id,
            str(exc),
        )
        return _json_error(
            500,
            request_id,
            "Internal server error while processing the profile submission.",
            "internal_error",
            destination_channel="backend_exception",
        )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5501))
    app.run(debug=False, host="0.0.0.0", port=port)
