from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests
import tomllib
from packaging.requirements import Requirement

DEPENDENCY_ALERT = "dependabot"
CODE_SCANNING_ALERT = "code-scanning"
SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}
NON_PRODUCTION_PREFIXES = ("tests/", "docs/", "scripts/", "playbook/")


@dataclass
class AlertAssessment:
    alert_type: str
    number: int
    title: str
    package_or_rule: str
    severity: str
    affected_paths: list[str]
    blast_radius: str
    action: str
    reachable: bool
    fix_version: str | None


class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str) -> None:
        self._owner = owner
        self._repo = repo
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def _url(self, path: str) -> str:
        return f"https://api.github.com{path}"

    def paginate(self, path: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        page = 1
        while True:
            response = self._session.get(
                self._url(path), params={"per_page": 100, "page": page}, timeout=30
            )
            response.raise_for_status()
            payload = response.json()
            if not payload:
                break
            if isinstance(payload, list):
                results.extend(payload)
            else:
                break
            page += 1
        return results

    def request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        response = self._session.request(
            method, self._url(path), json=payload, timeout=30
        )
        response.raise_for_status()
        if not response.content:
            return {}
        data: dict[str, Any] = response.json()
        return data

    def find_open_daily_issue(self) -> dict[str, Any] | None:
        issues = self.paginate(f"/repos/{self._owner}/{self._repo}/issues?state=open")
        for issue in issues:
            if issue.get("pull_request"):
                continue
            if issue.get("title") == "Daily Security Report":
                return issue
        return None

    def upsert_daily_issue(self, body: str) -> None:
        existing = self.find_open_daily_issue()
        if existing is not None:
            self.request(
                "PATCH",
                f"/repos/{self._owner}/{self._repo}/issues/{existing['number']}",
                {"body": body},
            )
            return
        self.request(
            "POST",
            f"/repos/{self._owner}/{self._repo}/issues",
            {"title": "Daily Security Report", "body": body},
        )

    def create_dependabot_comment(self, alert_number: int, body: str) -> None:
        self.request(
            "POST",
            f"/repos/{self._owner}/{self._repo}/dependabot/alerts/{alert_number}/comments",
            {"body": body},
        )

    def get_default_branch(self) -> str:
        repo = self.request("GET", f"/repos/{self._owner}/{self._repo}")
        return str(repo["default_branch"])

    def create_dependency_update_pr(
        self,
        *,
        alert: AlertAssessment,
        manifest_path: str,
        updated_content: str,
    ) -> None:
        default_branch = self.get_default_branch()
        base_ref = self.request(
            "GET", f"/repos/{self._owner}/{self._repo}/git/ref/heads/{default_branch}"
        )
        base_sha = str(base_ref["object"]["sha"])
        branch = f"security/dependabot-alert-{alert.number}-{sanitize_ref_name(alert.package_or_rule)}"

        try:
            self.request(
                "GET", f"/repos/{self._owner}/{self._repo}/git/ref/heads/{branch}"
            )
            return
        except requests.HTTPError as error:
            status = error.response.status_code if error.response is not None else 0
            if status != 404:
                raise

        self.request(
            "POST",
            f"/repos/{self._owner}/{self._repo}/git/refs",
            {"ref": f"refs/heads/{branch}", "sha": base_sha},
        )

        file_data = self.request(
            "GET",
            f"/repos/{self._owner}/{self._repo}/contents/{manifest_path}?ref={branch}",
        )
        sha = str(file_data["sha"])
        encoded = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

        self.request(
            "PUT",
            f"/repos/{self._owner}/{self._repo}/contents/{manifest_path}",
            {
                "message": f"chore(security): bump {alert.package_or_rule} to {alert.fix_version}",
                "content": encoded,
                "sha": sha,
                "branch": branch,
            },
        )

        self.request(
            "POST",
            f"/repos/{self._owner}/{self._repo}/pulls",
            {
                "title": f"chore(security): bump {alert.package_or_rule} to {alert.fix_version}",
                "head": branch,
                "base": default_branch,
                "body": (
                    f"Automated fix for Dependabot alert #{alert.number}.\n\n"
                    f"- Package: `{alert.package_or_rule}`\n"
                    f"- Fixed version: `{alert.fix_version}`\n"
                    f"- Manifest: `{manifest_path}`"
                ),
            },
        )


def sanitize_ref_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._/-]", "-", value).strip("-")


def parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def is_recent(alert: dict[str, Any], cutoff: datetime) -> bool:
    created_at = (
        parse_time(str(alert.get("created_at"))) if alert.get("created_at") else None
    )
    updated_at = (
        parse_time(str(alert.get("updated_at"))) if alert.get("updated_at") else None
    )
    timestamps = [value for value in (created_at, updated_at) if value is not None]
    return any(value >= cutoff for value in timestamps)


def detect_package_scope(manifest_path: Path, package_name: str) -> str:
    normalized = package_name.lower()
    if manifest_path.name == "package.json":
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        dependencies = data.get("dependencies", {})
        dev_dependencies = data.get("devDependencies", {})
        if normalized in {name.lower() for name in dependencies}:
            return "prod"
        if normalized in {name.lower() for name in dev_dependencies}:
            return "dev"
        return "unknown"

    if manifest_path.name == "pyproject.toml":
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        for requirement in project.get("dependencies", []):
            if Requirement(str(requirement)).name.lower() == normalized:
                return "prod"
        groups = data.get("dependency-groups", {})
        for group_name, requirements in groups.items():
            for requirement in requirements:
                if Requirement(str(requirement)).name.lower() == normalized:
                    return "dev" if group_name == "dev" else "optional"
        return "unknown"

    return "unknown"


def search_repo_for_package(repo_root: Path, package_name: str) -> list[str]:
    matches: list[str] = []
    needle = package_name.lower()
    for path in repo_root.rglob("*"):
        if not path.is_file() or any(part.startswith(".") for part in path.parts):
            continue
        if any(part in {"node_modules", "build", ".venv"} for part in path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if needle in content.lower():
            matches.append(str(path.relative_to(repo_root)))
        if len(matches) >= 5:
            break
    return matches


def compute_blast_radius(
    severity: str, reachable: bool, path_hint: str | None = None
) -> str:
    if not reachable:
        return "low"
    if path_hint and any(
        path_hint.startswith(prefix) for prefix in NON_PRODUCTION_PREFIXES
    ):
        return "low"
    if severity in {"critical", "high"}:
        return "high"
    if severity == "medium":
        return "medium"
    return "low"


def assess_dependabot_alert(alert: dict[str, Any], repo_root: Path) -> AlertAssessment:
    advisory = alert.get("security_advisory", {})
    dependency = alert.get("dependency", {})
    package = dependency.get("package", {}).get("name", "unknown")
    manifest_path = dependency.get("manifest_path", "")
    severity = str(advisory.get("severity", "low")).lower()
    scope = (
        detect_package_scope(repo_root / manifest_path, package)
        if manifest_path
        else "unknown"
    )
    reachable = scope == "prod"
    blast_radius = compute_blast_radius(severity, reachable)
    fix = (
        alert.get("security_vulnerability", {})
        .get("first_patched_version", {})
        .get("identifier")
    )
    affected_paths = [manifest_path] if manifest_path else []
    affected_paths.extend(
        path
        for path in search_repo_for_package(repo_root, package)
        if path not in affected_paths
    )
    if blast_radius == "low":
        action = "low risk"
    elif fix:
        action = f"upgrade to {fix}"
    else:
        action = "no fix"
    return AlertAssessment(
        alert_type=DEPENDENCY_ALERT,
        number=int(alert["number"]),
        title=str(advisory.get("summary", package)),
        package_or_rule=package,
        severity=severity,
        affected_paths=affected_paths,
        blast_radius=blast_radius,
        action=action,
        reachable=reachable,
        fix_version=str(fix) if fix else None,
    )


def assess_code_scanning_alert(alert: dict[str, Any]) -> AlertAssessment:
    rule = alert.get("rule", {})
    severity = str(
        rule.get("severity")
        or alert.get("rule", {}).get("security_severity_level")
        or "low"
    ).lower()
    location = alert.get("most_recent_instance", {}).get("location", {})
    path = str(location.get("path", ""))
    reachable = bool(path) and not any(
        path.startswith(prefix) for prefix in NON_PRODUCTION_PREFIXES
    )
    blast_radius = compute_blast_radius(severity, reachable, path)
    title = str(rule.get("description") or rule.get("id") or "Code scanning alert")
    action = "low risk" if blast_radius == "low" else "no fix"
    return AlertAssessment(
        alert_type=CODE_SCANNING_ALERT,
        number=int(alert["number"]),
        title=title,
        package_or_rule=str(rule.get("id", "rule")),
        severity=severity,
        affected_paths=[path] if path else [],
        blast_radius=blast_radius,
        action=action,
        reachable=reachable,
        fix_version=None,
    )


def select_relevant_alerts(alerts: list[AlertAssessment]) -> list[AlertAssessment]:
    def sort_key(alert: AlertAssessment) -> tuple[int, int]:
        return (
            SEVERITY_WEIGHT.get(alert.severity, 0),
            1 if alert.blast_radius == "high" else 0,
        )

    return sorted(
        [
            alert
            for alert in alerts
            if alert.blast_radius in {"high", "medium"} and alert.reachable
        ],
        key=sort_key,
        reverse=True,
    )


def render_daily_issue(alerts: list[AlertAssessment]) -> str:
    lines: list[str] = []
    icon_by_blast = {"high": "🔴", "medium": "🟠", "low": "🟡"}
    for alert in alerts:
        affected = ", ".join(alert.affected_paths) if alert.affected_paths else "N/A"
        lines.extend(
            [
                f"- {icon_by_blast.get(alert.blast_radius, '🟡')} **[{alert.blast_radius}] {alert.package_or_rule}**",
                f"  - Affected: {affected}",
                f"  - Blast radius: {'reachable in production paths' if alert.reachable else 'unreachable in production'}",
                f"  - Action: {alert.action}",
            ]
        )
    return "\n".join(lines)


def update_manifest_if_possible(
    alert: AlertAssessment, manifest_path: Path
) -> str | None:
    if alert.fix_version is None:
        return None
    if manifest_path.name == "package.json":
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        dependencies = data.get("dependencies", {})
        if alert.package_or_rule not in dependencies:
            return None
        new_value = f"^{alert.fix_version}"
        if dependencies.get(alert.package_or_rule) == new_value:
            return None
        dependencies[alert.package_or_rule] = new_value
        data["dependencies"] = dependencies
        return f"{json.dumps(data, indent=4)}\n"

    if manifest_path.name == "pyproject.toml":
        content = manifest_path.read_text(encoding="utf-8")
        data = tomllib.loads(content)
        for requirement_text in data.get("project", {}).get("dependencies", []):
            requirement = Requirement(str(requirement_text))
            if requirement.name.lower() != alert.package_or_rule.lower():
                continue
            extras = (
                f"[{','.join(sorted(requirement.extras))}]"
                if requirement.extras
                else ""
            )
            marker = f"; {requirement.marker}" if requirement.marker else ""
            new_requirement = f"{requirement.name}{extras}>={alert.fix_version}{marker}"
            return content.replace(f'"{requirement_text}"', f'"{new_requirement}"', 1)
    return None


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["GITHUB_REPOSITORY"]
    owner, repo = repository.split("/", maxsplit=1)
    repo_root = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
    cutoff = datetime.now(tz=UTC) - timedelta(hours=24)

    client = GitHubClient(token, owner, repo)
    dependabot_alerts = client.paginate(
        f"/repos/{owner}/{repo}/dependabot/alerts?state=open"
    )
    code_scanning_alerts = client.paginate(
        f"/repos/{owner}/{repo}/code-scanning/alerts?state=open"
    )

    assessments: list[AlertAssessment] = []
    for dependabot_alert in dependabot_alerts:
        if is_recent(dependabot_alert, cutoff):
            assessments.append(assess_dependabot_alert(dependabot_alert, repo_root))
    for code_scanning_alert in code_scanning_alerts:
        if is_recent(code_scanning_alert, cutoff):
            assessments.append(assess_code_scanning_alert(code_scanning_alert))

    relevant = select_relevant_alerts(assessments)
    for alert in relevant:
        if alert.alert_type != DEPENDENCY_ALERT:
            continue
        original = next(
            item for item in dependabot_alerts if int(item["number"]) == alert.number
        )
        manifest_rel = str(original.get("dependency", {}).get("manifest_path", ""))
        if not manifest_rel:
            continue
        manifest_path = repo_root / manifest_rel
        if not manifest_path.exists():
            continue
        updated_content = update_manifest_if_possible(alert, manifest_path)
        if updated_content is not None:
            client.create_dependency_update_pr(
                alert=alert, manifest_path=manifest_rel, updated_content=updated_content
            )
            continue
        if alert.fix_version is None:
            client.create_dependabot_comment(
                alert.number,
                "Reachable production exposure confirmed. No fix version is currently available.",
            )

    if relevant:
        client.upsert_daily_issue(render_daily_issue(relevant))


if __name__ == "__main__":
    main()
