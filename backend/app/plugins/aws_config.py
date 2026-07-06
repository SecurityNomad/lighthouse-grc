"""AWS Config / Security Hub plugin.

Pulls non-compliant AWS Config rule evaluations and Security Hub findings and
imports them into the Risk Register. Runs in two modes:

  * demo (default): uses bundled sample findings so the flow is demonstrable
    without AWS credentials — matches the WBS "live or mocked AWS endpoint".
  * live: lazily imports boto3 and queries the account in `aws_region`.

boto3 is intentionally not a hard dependency; live mode requires it installed
(`pip install boto3`) and standard AWS credentials in the environment.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.plugins.base import (
    RiskSourcePlugin,
    RiskCandidate,
    PluginRunResult,
    registry,
)
from app.schemas.plugin import PluginStatus

# AWS severity label → Lighthouse impact level.
_SEVERITY_TO_IMPACT = {
    "CRITICAL": "Critical",
    "HIGH": "High",
    "MEDIUM": "Medium",
    "LOW": "Low",
    "INFORMATIONAL": "Negligible",
}

# A small, representative set of findings for demo mode.
_SAMPLE_FINDINGS = [
    {
        "id": "config/s3-bucket-public-read-prohibited/my-data-bucket",
        "title": "S3 bucket allows public read access",
        "severity": "CRITICAL",
        "resource": "arn:aws:s3:::my-data-bucket",
        "rule": "s3-bucket-public-read-prohibited",
    },
    {
        "id": "config/encrypted-volumes/vol-0a1b2c3d",
        "title": "EBS volume is not encrypted",
        "severity": "HIGH",
        "resource": "vol-0a1b2c3d",
        "rule": "encrypted-volumes",
    },
    {
        "id": "securityhub/iam-root-access-key/root",
        "title": "Root account has an active access key",
        "severity": "CRITICAL",
        "resource": "AWS::::Account:root",
        "rule": "iam.4",
    },
    {
        "id": "config/rds-storage-encrypted/db-prod-1",
        "title": "RDS instance storage is not encrypted",
        "severity": "MEDIUM",
        "resource": "db-prod-1",
        "rule": "rds-storage-encrypted",
    },
    {
        "id": "config/cloudtrail-enabled/global",
        "title": "CloudTrail is not enabled in all regions",
        "severity": "HIGH",
        "resource": "AWS::CloudTrail",
        "rule": "cloudtrail-enabled",
    },
]


class AWSConfigPlugin(RiskSourcePlugin):
    name = "aws_config"
    display_name = "AWS Config / Security Hub"
    version = "1.0.0"
    description = (
        "Imports non-compliant AWS Config evaluations and Security Hub findings "
        "into the Risk Register."
    )

    def status(self) -> PluginStatus:
        if not settings.aws_plugin_enabled:
            return PluginStatus(configured=False, healthy=False, mode="disabled",
                                message="Plugin disabled via configuration.")
        if settings.aws_demo_mode:
            return PluginStatus(configured=True, healthy=True, mode="demo",
                                message="Demo mode — using bundled sample findings.")
        try:
            import boto3  # noqa: F401
        except ImportError:
            return PluginStatus(configured=False, healthy=False, mode="live",
                                message="Live mode requires boto3 (`pip install boto3`).")
        return PluginStatus(configured=True, healthy=True, mode="live",
                            message=f"Live mode — region {settings.aws_region}.")

    def _fetch_findings(self) -> List[dict]:
        if settings.aws_demo_mode:
            return list(_SAMPLE_FINDINGS)
        return self._fetch_live_findings()

    def _fetch_live_findings(self) -> List[dict]:  # pragma: no cover - needs AWS
        import boto3

        findings: List[dict] = []

        securityhub = boto3.client("securityhub", region_name=settings.aws_region)
        paginator = securityhub.get_paginator("get_findings")
        for page in paginator.paginate(
            Filters={"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]}
        ):
            for f in page.get("Findings", []):
                findings.append({
                    "id": f"securityhub/{f['Id']}",
                    "title": f.get("Title", "Security Hub finding"),
                    "severity": f.get("Severity", {}).get("Label", "MEDIUM"),
                    "resource": (f.get("Resources") or [{}])[0].get("Id", "unknown"),
                    "rule": f.get("GeneratorId", "securityhub"),
                })

        config = boto3.client("config", region_name=settings.aws_region)
        rules = config.describe_compliance_by_config_rule(
            ComplianceTypes=["NON_COMPLIANT"]
        )
        for r in rules.get("ComplianceByConfigRules", []):
            rule_name = r["ConfigRuleName"]
            findings.append({
                "id": f"config/{rule_name}",
                "title": f"AWS Config rule non-compliant: {rule_name}",
                "severity": "MEDIUM",
                "resource": rule_name,
                "rule": rule_name,
            })
        return findings

    async def collect(
        self, db: AsyncSession, client_id: Optional[uuid.UUID] = None
    ) -> PluginRunResult:
        from app.plugins.base import upsert_risks

        raw = self._fetch_findings()
        candidates = [
            RiskCandidate(
                external_id=f["id"],
                title=f["title"],
                description=(
                    f"Imported from AWS ({f['rule']}). Affected resource: {f['resource']}."
                ),
                impact=_SEVERITY_TO_IMPACT.get(f["severity"].upper(), "Medium"),
                likelihood="Likely",
                threat="Cloud misconfiguration",
                tags=["aws", "cloud", f["rule"]],
                owner="Cloud Security",
            )
            for f in raw
        ]
        return await upsert_risks(db, self.name, candidates, client_id)


registry.register(AWSConfigPlugin())
