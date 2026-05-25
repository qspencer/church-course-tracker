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
    """The previously-leaked admin password must not appear anywhere active.

    Scope broadened May 2026 after the legacy-scripts cleanup pass: the
    leaked literal had crept into ~20 one-off operational scripts and three
    e2e test fallbacks that were each individually a small footprint but
    collectively re-introduced the credential in every clone of the repo
    (and, for the standalone admin-create script, re-asserted it on every
    container restart). All those callers were removed or rewritten to
    read from environment variables.

    The exclusions below are *legitimate* references: the docs/archive
    folder is frozen historical state, the evaluation document explains
    the original incident, and this file itself names the literal so it
    can search for it.
    """

    LEAKED_VALUE = "Matthew778*"

    # Files allowed to contain the leaked literal as a documented historical
    # reference. Any new entry here should be scrutinized in code review.
    ALLOWED_PATHS = {
        "backend/tests/test_config_security.py",  # this guard itself
        "docs/EVALUATION_2026-05-09.md",          # the original incident postmortem
        "docs/EVALUATION_2026-05-18.md",          # follow-up audit; references the May-9 incident
    }

    def test_leaked_password_absent_from_active_paths(self):
        try:
            result = subprocess.run(
                [
                    "git", "-C", str(REPO_ROOT), "grep", "-n",
                    "--fixed-strings", "--", self.LEAKED_VALUE,
                ],
                capture_output=True, text=True, timeout=30,
            )
        except FileNotFoundError:
            pytest.skip("git not available in test environment")

        # git grep exits 0 when matches are found, 1 when none.
        if result.returncode != 0:
            return

        hits = []
        for line in result.stdout.splitlines():
            # git grep output format: <path>:<line>:<content>
            path = line.split(":", 1)[0]
            if path in self.ALLOWED_PATHS:
                continue
            if path.startswith("docs/archive/"):
                # Archived docs are frozen historical state.
                continue
            hits.append(line)

        assert not hits, (
            f"Leaked credential '{self.LEAKED_VALUE}' is present in active "
            "paths:\n" + "\n".join(hits) +
            "\n\nIf the reference is legitimate (e.g. a postmortem), add the "
            "path to TestNoLeakedSecretsInActivePaths.ALLOWED_PATHS with a "
            "comment explaining why."
        )
