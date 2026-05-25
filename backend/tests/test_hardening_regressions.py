"""
Defensive regression tests for the May 2026 hardening pass.

These are "negative-assertion" tests — they verify that things that USED to
be true are now NOT true. They pass trivially today but exist so that if
someone later reverts a hardening change without realizing why it was made,
CI fails loudly instead of letting the regression ship.

Each section documents the specific commit / behavior it locks in.
"""

import logging
import re

import pytest


# ===========================================================================
# 1. Auth gates on the 9 previously-unauthenticated endpoint modules
#     (May 2026 audit §3.1 B1-B9; closed in commit a875993)
# ===========================================================================
# The 2026-05-18 evaluation found that 9 endpoint modules accepted requests
# without any auth, exposing PII (people), anonymous CSV/PDF export
# (reports), and write paths on enrollments / progress / etc. We added
# Depends(get_current_active_user) to all of them. The existing tests in
# test_endpoints.py authenticate using the admin_token fixture, which
# verifies the routes work WITH auth - but they don't verify what happens
# WITHOUT auth, so a future revert of the auth dep would still pass them.
#
# The parametrized test below exercises 1-2 representative routes per
# module and asserts the unauthenticated response is 401 (or 403, which
# Starlette returns from some auth-flow paths).

AUTH_REQUIRED_ENDPOINTS = [
    # people.py - PII reads + admin-only writes
    ("GET", "/api/v1/people/"),
    ("GET", "/api/v1/people/1"),
    # reports.py - all six reporting routes (anonymous CSV/PDF export was
    # the worst finding in the audit)
    ("GET", "/api/v1/reports/dashboard"),
    ("GET", "/api/v1/reports/enrollment"),
    # courses.py - read endpoints; writes were already gated
    ("GET", "/api/v1/courses/"),
    ("GET", "/api/v1/courses/1"),
    # enrollments.py - reads + write-paths
    ("GET", "/api/v1/enrollments/"),
    ("GET", "/api/v1/enrollments/1"),
    # progress.py - all 7 routes
    ("GET", "/api/v1/progress/member/1"),
    ("GET", "/api/v1/progress/1"),
    # sync.py - admin-only sync trigger + auth-required status
    ("GET", "/api/v1/sync/status"),
    # autocomplete_suggestions.py - auth-required read, admin/staff write
    ("GET", "/api/v1/autocomplete-suggestions/location"),
]


@pytest.mark.parametrize("method,path", AUTH_REQUIRED_ENDPOINTS)
def test_endpoint_rejects_unauthenticated_request(client, method, path):
    """Removing the auth dep from any of these endpoints will fail this test.

    If this test breaks, check whether someone removed the
    `current_user: dict = Depends(get_current_active_user)` parameter from
    the handler. See commit a875993 for the original hardening rationale.
    """
    response = client.request(method, path)
    assert response.status_code in (401, 403), (
        f"{method} {path} returned {response.status_code} with no Authorization "
        f"header; expected 401 or 403. The auth dependency on this route may "
        f"have been removed."
    )


# ===========================================================================
# 2. Typo route POST /api/v1/authrefresh is NOT mounted
#     (May 2026, commit 2213a13)
# ===========================================================================
# auth.py:210 used to have `@router.post("refresh")` (missing leading slash)
# alongside the correct `@router.post("/refresh")`. FastAPI mounted both,
# producing a real route at POST /api/v1/authrefresh in addition to the
# intended /api/v1/auth/refresh. We removed the malformed decorator.

class TestAuthRefreshTypoRoute:
    def test_typo_route_authrefresh_returns_404(self, client):
        """POST /api/v1/authrefresh must not exist."""
        response = client.post("/api/v1/authrefresh")
        assert response.status_code == 404, (
            f"POST /api/v1/authrefresh returned {response.status_code}; "
            f"expected 404. The typo decorator at auth.py:210 may have been "
            f"re-introduced (look for @router.post(\"refresh\") with no "
            f"leading slash)."
        )

    def test_real_refresh_route_still_exists(self, client):
        """Sanity check: the legitimate /api/v1/auth/refresh route should
        still be mounted (returning 401 with no token, NOT 404)."""
        response = client.post("/api/v1/auth/refresh")
        assert response.status_code != 404, (
            f"POST /api/v1/auth/refresh returned 404; the legitimate "
            f"refresh route may have been accidentally removed."
        )


# ===========================================================================
# 3. get_current_user does NOT log the Authorization header or token preview
#     (May 2026, commit 2213a13)
# ===========================================================================
# auth.py:46-54 used to do:
#   logger.info(f"Authorization header received: {auth_preview}...")
#   logger.info(f"Extracted token: {token_preview}...")
# which shipped JWT prefixes to CloudWatch and Sentry on every authenticated
# request. We removed those lines. This test catches any reintroduction.

class TestTokenIsNotLoggedAtInfo:
    # Substrings that would indicate the lines have been re-added.
    FORBIDDEN_PATTERNS = [
        re.compile(r"Authorization header received", re.IGNORECASE),
        re.compile(r"Extracted token", re.IGNORECASE),
    ]

    def test_authenticated_request_does_not_log_token_at_info(
        self, caplog, client, admin_token
    ):
        """An authenticated request must not produce any INFO log line
        containing the Authorization-header preview or token preview.

        We hit a route that goes through get_current_user (any auth-required
        endpoint will do) and inspect captured logs for the forbidden
        patterns.
        """
        caplog.set_level(logging.INFO, logger="app.api.v1.endpoints.auth")
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.get("/api/v1/users/me", headers=headers)

        info_records = [r for r in caplog.records if r.levelno == logging.INFO]
        for record in info_records:
            message = record.getMessage()
            for pattern in self.FORBIDDEN_PATTERNS:
                assert not pattern.search(message), (
                    f"Found a token-logging pattern in INFO log: "
                    f"{message!r} (matched: {pattern.pattern!r}). "
                    f"The auth.py:46-54 token-logging lines may have been "
                    f"re-introduced; see commit 2213a13."
                )

        # Also: the actual token contents (or first 20 chars of it) should
        # never appear in any captured log record at any level.
        token_prefix = admin_token[:20]
        for record in caplog.records:
            assert token_prefix not in record.getMessage(), (
                f"Token prefix {token_prefix[:8]}... appears in log record "
                f"at level {record.levelname}: {record.getMessage()!r}. "
                f"No log statement should embed token content."
            )


# ===========================================================================
# 4. Mock Planning Center router is gated to non-production
#     (May 2026, commit a875993)
# ===========================================================================
# app/api/v1/api.py mounts mock_planning_center.router only when the
# _should_mount_mock_planning_center predicate returns True. The predicate
# was extracted from the inline `if` block specifically so it can be
# unit-tested here. If the gate is removed, the mock module's
# (unauthenticated) routes become reachable in production.

class TestMockPlanningCenterGate:
    @pytest.fixture(autouse=True)
    def _import_predicate(self):
        from app.api.v1.api import _should_mount_mock_planning_center
        self.predicate = _should_mount_mock_planning_center

    def test_production_with_mock_enabled_does_not_mount(self):
        """Even if USE_MOCK_PLANNING_CENTER is True, production must not
        mount the mock router. This is the primary regression target -
        the failure mode the audit was trying to prevent."""
        assert self.predicate("production", True) is False

    def test_production_with_mock_disabled_does_not_mount(self):
        assert self.predicate("production", False) is False

    def test_development_with_mock_enabled_does_mount(self):
        """Sanity check: the predicate isn't broken in the obvious case."""
        assert self.predicate("development", True) is True

    def test_development_with_mock_disabled_does_not_mount(self):
        """Even outside production, the mock requires explicit opt-in."""
        assert self.predicate("development", False) is False

    def test_staging_like_environment_with_mock_enabled_does_mount(self):
        """Any environment that isn't literally 'production' should be
        treated as non-prod by the predicate (no surprise allowlist)."""
        assert self.predicate("staging", True) is True
        assert self.predicate("test", True) is True
        assert self.predicate("", True) is True
