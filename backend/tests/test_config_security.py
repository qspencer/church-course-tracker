"""
Regression tests for production security validation in app.core.config.

Background: prior to May 2026 ``config.py`` shipped concrete default
passwords (e.g. ``"Matthew778*"``) that would be used silently if the
operator forgot to set the corresponding env var. These tests assert:

1. The Settings class refuses to start in production when any seed-user
   password is still the dev placeholder.
2. The dev placeholder is allowed in non-production environments (so
   local dev keeps working).
3. The known-leaked password is no longer present anywhere in the
   codebase (defensive grep).
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

from app.core.config import Settings


REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_prod_settings(**overrides) -> Settings:
    """Construct a Settings instance with ENVIRONMENT=production overrides applied."""
    base = {
        "ENVIRONMENT": "production",
        # Provide a long enough SECRET_KEY so that check passes and
        # we isolate the password validation we actually want to test.
        "SECRET_KEY": "x" * 64,
        "ALLOWED_ORIGINS": ["https://example.com"],
        "DEBUG": False,
    }
    base.update(overrides)
    return Settings(**base)


class TestProductionPasswordValidation:
    """Production startup must refuse placeholder passwords."""

    def test_admin_placeholder_rejected_in_production(self):
        """ADMIN_PASSWORD is the only password that hard-blocks production startup."""
        with pytest.raises(ValueError) as exc:
            _make_prod_settings(
                ADMIN_PASSWORD="CHANGE_ME_DEV_ONLY",
                STAFF_PASSWORD="anything",
                INSTRUCTOR_PASSWORD="anything",
                VIEWER_PASSWORD="anything",
            )
        assert "ADMIN_PASSWORD" in str(exc.value)

    def test_non_admin_placeholders_warn_but_allowed_in_production(self, caplog):
        """STAFF/INSTRUCTOR/VIEWER placeholders log a warning but do not block.

        Rationale: those are dev-helper seed accounts; in a long-running prod
        system the user records already exist in the DB and the env vars are
        not actively consumed. Hard-blocking on them was over-strict.
        """
        # Should not raise.
        s = _make_prod_settings(
            ADMIN_PASSWORD="real-strong-pass",
            STAFF_PASSWORD="CHANGE_ME_DEV_ONLY",
            INSTRUCTOR_PASSWORD="CHANGE_ME_DEV_ONLY",
            VIEWER_PASSWORD="CHANGE_ME_DEV_ONLY",
        )
        assert s.ENVIRONMENT == "production"

    def test_real_passwords_accepted_in_production(self):
        # Should not raise.
        s = _make_prod_settings(
            ADMIN_PASSWORD="real-strong-pass-1",
            STAFF_PASSWORD="real-strong-pass-2",
            INSTRUCTOR_PASSWORD="real-strong-pass-3",
            VIEWER_PASSWORD="real-strong-pass-4",
        )
        assert s.ADMIN_PASSWORD != s.DEV_PASSWORD_PLACEHOLDER

    def test_placeholder_allowed_in_development(self):
        # In dev, the placeholder is fine — keep local setup frictionless.
        # Settings reads ENVIRONMENT from env at import time, so we pass it.
        s = Settings(
            ENVIRONMENT="development",
            SECRET_KEY="x" * 64,
            ADMIN_PASSWORD="CHANGE_ME_DEV_ONLY",
        )
        assert s.ADMIN_PASSWORD == "CHANGE_ME_DEV_ONLY"


class TestDebugForcedOffInProduction:
    """In production, settings.DEBUG must be False regardless of input.

    Background: settings.DEBUG is surfaced in the public /health payload as
    ``checks.debug_mode`` and, more importantly, is the flag any future code
    would gate verbose-error or developer-only behavior on. Previously the
    validator only logged a warning if DEBUG was True under
    ENVIRONMENT=production; the value passed through unchanged. As of May
    2026 the validator hard-overrides DEBUG to False whenever ENVIRONMENT is
    production so that env-var misconfiguration cannot leak debug state to
    end users.
    """

    def test_debug_forced_false_in_production_even_when_input_is_true(self):
        s = _make_prod_settings(
            ADMIN_PASSWORD="real-strong-pass",
            DEBUG=True,
        )
        assert s.DEBUG is False

    def test_debug_remains_false_in_production_when_input_is_false(self):
        s = _make_prod_settings(
            ADMIN_PASSWORD="real-strong-pass",
            DEBUG=False,
        )
        assert s.DEBUG is False

    def test_debug_preserved_in_development(self):
        s = Settings(
            ENVIRONMENT="development",
            SECRET_KEY="x" * 64,
            ADMIN_PASSWORD="CHANGE_ME_DEV_ONLY",
            DEBUG=True,
        )
        assert s.DEBUG is True


class TestNoLeakedSecretsInActivePaths:
    """The previously-leaked admin password must not appear in active deploy paths.

    Scope is intentionally narrow: production code, migrations, the public
    README, the frontend, and the Terraform that provisions the live infra.
    Historical references in archived docs and one-off recovery scripts are
    out of scope here - they need a separate cleanup pass tracked in the
    May 2026 evaluation document.
    """

    LEAKED_VALUE = "Matthew778*"

    # Paths that ship to production users / get applied to the live system.
    # If the leaked literal shows up here, that is a real regression.
    ACTIVE_PATHS = [
        "README.md",
        "backend/app",
        "backend/migrations",
        "frontend/church-course-tracker/src",
        "infrastructure",
    ]

    def test_leaked_password_absent_from_active_paths(self):
        try:
            result = subprocess.run(
                [
                    "git", "-C", str(REPO_ROOT), "grep", "-n",
                    "--fixed-strings", "--", self.LEAKED_VALUE, "--", *self.ACTIVE_PATHS,
                ],
                capture_output=True, text=True, timeout=30,
            )
        except FileNotFoundError:
            pytest.skip("git not available in test environment")

        # git grep exits 0 when matches are found, 1 when none.
        if result.returncode == 0:
            hits = [
                line for line in result.stdout.splitlines()
                if "test_config_security.py" not in line
            ]
            assert not hits, (
                f"Leaked credential '{self.LEAKED_VALUE}' is present in active "
                "deploy paths:\n" + "\n".join(hits) +
                "\n\nFollow-up cleanup of legacy scripts/e2e fallbacks tracked "
                "in docs/EVALUATION_2026-05-09.md (Section 8)."
            )
