from __future__ import annotations

import json
from pathlib import Path

from scripts.daily_security_report import (
    AlertAssessment,
    compute_blast_radius,
    detect_package_scope,
    render_daily_issue,
    select_relevant_alerts,
    update_manifest_if_possible,
)


def test_detect_package_scope_from_package_json(tmp_path: Path) -> None:
    manifest = tmp_path / "package.json"
    manifest.write_text(
        json.dumps(
            {
                "dependencies": {"lodash": "^4.17.20"},
                "devDependencies": {"jest": "^29.0.0"},
            }
        ),
        encoding="utf-8",
    )

    assert detect_package_scope(manifest, "lodash") == "prod"
    assert detect_package_scope(manifest, "jest") == "dev"


def test_detect_package_scope_from_pyproject(tmp_path: Path) -> None:
    manifest = tmp_path / "pyproject.toml"
    manifest.write_text(
        """
[project]
dependencies = ["requests>=2.31.0"]

[dependency-groups]
dev = ["pytest>=8.0.0"]
""".strip(),
        encoding="utf-8",
    )

    assert detect_package_scope(manifest, "requests") == "prod"
    assert detect_package_scope(manifest, "pytest") == "dev"


def test_select_relevant_alerts_ignores_low_blast() -> None:
    alerts = [
        AlertAssessment(
            alert_type="dependabot",
            number=1,
            title="critical",
            package_or_rule="pkg-high",
            severity="high",
            affected_paths=["package.json"],
            blast_radius="high",
            action="upgrade",
            reachable=True,
            fix_version="1.2.3",
        ),
        AlertAssessment(
            alert_type="dependabot",
            number=2,
            title="low",
            package_or_rule="pkg-low",
            severity="high",
            affected_paths=["tests/test.py"],
            blast_radius="low",
            action="low risk",
            reachable=False,
            fix_version=None,
        ),
    ]

    relevant = select_relevant_alerts(alerts)

    assert [alert.number for alert in relevant] == [1]


def test_update_manifest_if_possible_for_package_json(tmp_path: Path) -> None:
    manifest = tmp_path / "package.json"
    manifest.write_text(
        json.dumps({"dependencies": {"lodash": "^4.17.20"}}), encoding="utf-8"
    )

    alert = AlertAssessment(
        alert_type="dependabot",
        number=7,
        title="lodash",
        package_or_rule="lodash",
        severity="high",
        affected_paths=["package.json"],
        blast_radius="high",
        action="upgrade",
        reachable=True,
        fix_version="4.17.21",
    )

    updated = update_manifest_if_possible(alert, manifest)

    assert updated is not None
    assert '"lodash": "^4.17.21"' in updated


def test_render_daily_issue_uses_required_format() -> None:
    issue = render_daily_issue(
        [
            AlertAssessment(
                alert_type="code-scanning",
                number=5,
                title="alert",
                package_or_rule="py/sql-injection",
                severity="high",
                affected_paths=["renumics/spotlight/backend/app.py"],
                blast_radius="high",
                action="no fix",
                reachable=True,
                fix_version=None,
            )
        ]
    )

    assert "- 🔴 **[high] py/sql-injection**" in issue
    assert "- Affected: renumics/spotlight/backend/app.py" in issue
    assert "- Blast radius:" in issue
    assert "- Action: no fix" in issue


def test_compute_blast_radius_marks_non_production_path_low() -> None:
    assert compute_blast_radius("high", True, "tests/unit/test_example.py") == "low"
