"""Generate a starter threat model with example threats for each STRIDE category."""
from __future__ import annotations

from typing import List

from .model import (
    App, Component, ComponentType, Severity, Stride,
    Threat, ThreatModel, TrustBoundary,
)


# One illustrative threat per STRIDE category — user edits these to fit their app.
_STRIDE_EXAMPLES = [
    {
        "stride": Stride.spoofing,
        "title": "Unauthenticated access to privileged endpoint",
        "description": (
            "An attacker presents forged or stolen credentials to impersonate a "
            "legitimate user or service."
        ),
        "severity": Severity.high,
        "mitigations": [
            "Enforce strong authentication (MFA where possible).",
            "Validate tokens server-side on every request.",
        ],
        "test_cases": [
            "Send requests with expired / tampered JWTs — expect 401.",
            "Replay a valid token after logout — expect 401.",
        ],
    },
    {
        "stride": Stride.tampering,
        "title": "Manipulation of data in transit or at rest",
        "description": (
            "An attacker modifies data while it travels between components or "
            "alters stored records without authorisation."
        ),
        "severity": Severity.high,
        "mitigations": [
            "Enforce TLS for all inter-service traffic.",
            "Apply HMAC or digital signatures to sensitive payloads.",
        ],
        "test_cases": [
            "Intercept a request via proxy and modify a field — expect rejection or integrity error.",
            "Directly modify a DB row and verify the application detects it on next read.",
        ],
    },
    {
        "stride": Stride.repudiation,
        "title": "Insufficient audit trail for sensitive actions",
        "description": (
            "A user performs a destructive or high-value action (e.g. deletion, "
            "privilege change) and the system lacks the logging to prove it."
        ),
        "severity": Severity.medium,
        "mitigations": [
            "Log actor, action, resource, and timestamp for all sensitive operations.",
            "Ship logs to a write-once or append-only store outside the app's trust boundary.",
        ],
        "test_cases": [
            "Perform a delete action and verify a log entry is created with the correct actor.",
            "Confirm logs are not accessible/modifiable by the actor who generated them.",
        ],
    },
    {
        "stride": Stride.information_disclosure,
        "title": "Sensitive data leaked in API responses or error messages",
        "description": (
            "Error messages, verbose responses, or improperly scoped queries expose "
            "data the caller is not authorised to see."
        ),
        "severity": Severity.medium,
        "mitigations": [
            "Return generic error messages to clients; log detail server-side only.",
            "Apply per-field authorisation — never return more than the caller's role permits.",
        ],
        "test_cases": [
            "Trigger a 500 error and inspect the response body for stack traces or internal paths.",
            "Call a resource endpoint as a low-privilege user and check for data belonging to other users.",
        ],
    },
    {
        "stride": Stride.denial_of_service,
        "title": "Resource exhaustion via unauthenticated or unbounded requests",
        "description": (
            "An attacker floods an endpoint with requests, or submits pathologically "
            "large inputs, causing the service to become unavailable."
        ),
        "severity": Severity.medium,
        "mitigations": [
            "Apply rate limiting and request-size caps at the edge.",
            "Paginate and stream large result sets rather than buffering in memory.",
        ],
        "test_cases": [
            "Send 1 000 requests per second to a public endpoint and verify rate-limit responses (429).",
            "Submit a multi-GB payload and confirm the server rejects it before processing.",
        ],
    },
    {
        "stride": Stride.elevation_of_privilege,
        "title": "Horizontal or vertical privilege escalation via IDOR or role bypass",
        "description": (
            "A lower-privileged user accesses or modifies resources that should be "
            "restricted to a higher-privilege role or a different user."
        ),
        "severity": Severity.high,
        "mitigations": [
            "Enforce authorisation checks server-side on every action, not just the UI.",
            "Use opaque, non-sequential resource identifiers.",
        ],
        "test_cases": [
            "As user A, request user B's resource by substituting B's ID — expect 403.",
            "Call an admin endpoint with a standard-user token — expect 403.",
        ],
    },
]


def build_scaffold(
    name: str,
    description: str = "",
    repo: str = "",
    owner: str = "",
    component_specs: List[str] | None = None,
) -> ThreatModel:
    """
    Return a ThreatModel populated with one illustrative STRIDE threat per category.

    *component_specs* is a list of ``"type:id:name"`` strings, e.g.
    ``["api:backend:Backend API", "database:db:Primary DB"]``.
    Defaults to a single generic ``api`` component if omitted.
    """
    components: List[Component] = []

    if component_specs:
        for spec in component_specs:
            parts = spec.split(":", 2)
            if len(parts) == 3:
                ctype, cid, cname = parts
            elif len(parts) == 2:
                ctype, cid = parts
                cname = cid
            else:
                cid = spec
                ctype = "other"
                cname = spec
            components.append(
                Component(id=cid, name=cname, type=ComponentType(ctype))
            )
    else:
        components = [
            Component(id="app", name=name, type=ComponentType.api)
        ]

    # All example threats reference the first component by default.
    first_id = components[0].id

    threats = [
        Threat(
            id=f"T-{i + 1:03d}",
            components=[first_id],
            **{k: v for k, v in ex.items()},
        )
        for i, ex in enumerate(_STRIDE_EXAMPLES)
    ]

    return ThreatModel(
        version="1",
        app=App(
            name=name,
            description=description or None,
            repo=repo or None,
            owner=owner or None,
        ),
        components=components,
        trust_boundaries=[],
        threats=threats,
    )
