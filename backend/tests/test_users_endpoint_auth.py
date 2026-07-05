"""
Regression tests for authentication on /api/v1/users endpoints.

Background: prior to May 2026 the `GET /users` and `GET /users/{user_id}`
endpoints had no `Depends(get_current_active_user)` and would respond with
the full user list (or any user record) to unauthenticated callers. These
tests assert that both endpoints now require authentication and that other
already-protected endpoints continue to require it.
"""

import pytest
from fastapi.testclient import TestClient


class TestUsersEndpointAuthentication:
    """Every GET on /api/v1/users must require authentication."""

    def test_list_users_rejects_unauthenticated(self, client: TestClient):
        """Anonymous GET /api/v1/users/ must return 401, not the user list."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 401, (
            f"Expected 401 for anonymous /users/, got {response.status_code}. "
            "Regression: this endpoint was previously unauthenticated."
        )

    def test_list_users_rejects_unauthenticated_no_slash(self, client: TestClient):
        """The router declares both '' and '/' for the list — both must be guarded."""
        response = client.get("/api/v1/users")
        # FastAPI redirects to the trailing-slash form, but the protected
        # endpoint must still ultimately respond 401, never 200.
        assert response.status_code in (401, 307, 308), (
            f"Expected 401 (or redirect) for anonymous /users, got {response.status_code}."
        )
        if response.status_code in (307, 308):
            redirected = client.get(response.headers["location"])
            assert redirected.status_code == 401

    def test_get_user_by_id_rejects_unauthenticated(self, client: TestClient):
        """Anonymous GET /api/v1/users/{id} must return 401, not a user record."""
        response = client.get("/api/v1/users/1")
        assert response.status_code == 401, (
            f"Expected 401 for anonymous /users/1, got {response.status_code}. "
            "Regression: this endpoint was previously unauthenticated."
        )

    def test_list_users_accepts_authenticated(
        self, client: TestClient, admin_token: str
    ):
        """A valid token gets through (we don't care about role here, just auth)."""
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # Either 200 (authorized) or 403 (would-be authorized but role-restricted)
        # is acceptable — the failure case we're guarding against is 200 without auth.
        assert response.status_code in (200, 403), (
            f"Expected 200 or 403 for authenticated /users/, got {response.status_code}."
        )


class TestOtherUsersEndpointsStillProtected:
    """Sanity check that the endpoints we did NOT touch still require auth."""

    @pytest.mark.parametrize(
        "method,path",
        [
            ("get", "/api/v1/users/me"),
            ("post", "/api/v1/users/"),
            ("post", "/api/v1/users/bulk-delete"),
        ],
    )
    def test_endpoint_rejects_unauthenticated(
        self, client: TestClient, method: str, path: str
    ):
        kwargs = {"json": {}} if method != "get" else {}
        response = getattr(client, method)(path, **kwargs)
        assert response.status_code == 401, (
            f"Expected 401 for anonymous {method.upper()} {path}, "
            f"got {response.status_code}."
        )


class TestImportFromPCAuthorization:
    """Regression tests for POST /users/import-from-pc (fixed July 2026).

    Background: this endpoint previously required only an authenticated
    user (any role) and accepted an unvalidated `role` field, so any
    viewer could create an account with role="admin".
    """

    def test_import_rejects_unauthenticated(self, client: TestClient):
        response = client.post(
            "/api/v1/users/import-from-pc",
            json={"planning_center_person_id": "123", "role": "viewer"},
        )
        assert response.status_code == 401

    @pytest.mark.parametrize("token_fixture", ["staff_token", "viewer_token"])
    def test_import_rejects_non_admin(
        self, client: TestClient, token_fixture: str, request
    ):
        """Staff and viewer roles must get 403, exactly like POST /users."""
        token = request.getfixturevalue(token_fixture)
        response = client.post(
            "/api/v1/users/import-from-pc",
            json={"planning_center_person_id": "123", "role": "admin"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403, (
            f"Expected 403 for {token_fixture} on import-from-pc, "
            f"got {response.status_code}. Regression: non-admins could "
            "previously create accounts with arbitrary roles."
        )

    def test_import_rejects_invalid_role_value(
        self, client: TestClient, admin_token: str
    ):
        """The role field must be constrained to the known role names."""
        response = client.post(
            "/api/v1/users/import-from-pc",
            json={"planning_center_person_id": "123", "role": "superuser"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422, (
            f"Expected 422 for invalid role value, got {response.status_code}. "
            "Regression: arbitrary role strings were previously accepted."
        )
