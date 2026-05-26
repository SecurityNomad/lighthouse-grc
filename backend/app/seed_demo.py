"""
Demo data seed — Savanna Commercial Bank Limited (Nairobi, Kenya).

A mid-tier Kenyan commercial bank regulated by the Central Bank of Kenya (CBK),
processing M-Pesa payments via Safaricom API, operating Oracle FLEXCUBE as its
core banking system, and pursuing ISO 27001 certification.

Idempotent: gated on the presence of a sentinel risk title.
Activated by setting SEED_DEMO_DATA=true in the environment.
"""
import logging
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk import Risk, IMPACT_SCORE_MAP, LIKELIHOOD_SCORE_MAP
from app.models.control import Control, Framework
from app.models.control_mapping import RiskControl
from app.models.evidence import Evidence
from app.models.tprm import Vendor, VendorAssessment
from app.models.audit import AuditPlan, AuditItem, AuditFinding

logger = logging.getLogger(__name__)

_SENTINEL = "M-Pesa API fraud — unauthorised fund transfers via compromised integration credentials"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _risk(title, description, threat, impact, likelihood, treatment, owner, status,
          tags=None, treatment_notes=None, review_date=None,
          residual_impact=None, residual_likelihood=None):
    i_score = IMPACT_SCORE_MAP.get(impact, 3)
    l_score = LIKELIHOOD_SCORE_MAP.get(likelihood, 3)
    return Risk(
        id=uuid.uuid4(),
        title=title,
        description=description,
        threat=threat,
        impact=impact,
        likelihood=likelihood,
        treatment=treatment,
        treatment_notes=treatment_notes,
        owner=owner,
        status=status,
        tags=tags or [],
        review_date=review_date,
        impact_score=i_score,
        likelihood_score=l_score,
        risk_score=i_score * l_score,
        residual_impact_score=IMPACT_SCORE_MAP.get(residual_impact) if residual_impact else None,
        residual_likelihood_score=LIKELIHOOD_SCORE_MAP.get(residual_likelihood) if residual_likelihood else None,
        residual_risk_score=(
            IMPACT_SCORE_MAP[residual_impact] * LIKELIHOOD_SCORE_MAP[residual_likelihood]
            if residual_impact and residual_likelihood else None
        ),
    )


def _evidence(title, description, file_name, file_size, mime_type, expiry_date=None):
    return Evidence(
        id=uuid.uuid4(),
        title=title,
        description=description,
        file_name=file_name,
        file_path=f"/app/uploads/demo_{file_name}",
        file_size=file_size,
        mime_type=mime_type,
        expiry_date=expiry_date,
    )


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

async def seed_demo_data(session: AsyncSession) -> None:
    existing = await session.execute(select(Risk).where(Risk.title == _SENTINEL))
    if existing.scalar_one_or_none():
        logger.debug("Demo data already present — skipping")
        return

    logger.info("Seeding Savanna Commercial Bank demo data…")

    # ------------------------------------------------------------------
    # 1. Risks
    # ------------------------------------------------------------------
    risks = [
        # ---- R-01 ----
        _risk(
            title=_SENTINEL,
            description=(
                "Attackers obtain Savanna Bank's M-Pesa Daraja API consumer key and secret "
                "through insecure storage in source code or CI/CD variables, enabling "
                "fraudulent B2C disbursements from the bank's float account."
            ),
            threat="API credential compromise / supply chain",
            impact="Critical", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Rotating Daraja credentials to AWS Secrets Manager. Implementing webhook "
                "signature verification and IP allowlisting for Safaricom callback URLs. "
                "Real-time alert on float balance drops >KES 50,000."
            ),
            owner="Head of Digital Banking",
            status="In Treatment",
            tags=["m-pesa", "api", "fraud", "digital-banking"],
            review_date=date(2026, 8, 31),
            residual_impact="High", residual_likelihood="Unlikely",
        ),
        # ---- R-02 ----
        _risk(
            title="FLEXCUBE core banking outage during month-end processing",
            description=(
                "Oracle FLEXCUBE database server failure or network disruption during the "
                "peak month-end salary crediting window (last working day 16:00–20:00 EAT) "
                "prevents interbank RTGS settlements, triggering CBK SLA penalties and "
                "customer complaints."
            ),
            threat="Infrastructure failure / availability",
            impact="High", likelihood="Unlikely",
            treatment="Mitigate",
            treatment_notes=(
                "Active-passive failover to DR site in Upper Hill configured. "
                "Monthly DR switchover test now mandatory. "
                "Oracle Premier Support contract renewed until 2028."
            ),
            owner="Chief Technology Officer",
            status="In Treatment",
            tags=["core-banking", "flexcube", "availability", "rtgs"],
            review_date=date(2026, 9, 30),
            residual_impact="Medium", residual_likelihood="Rare",
        ),
        # ---- R-03 ----
        _risk(
            title="ATM skimming — card data and PIN capture across branch network",
            description=(
                "Criminal gangs install skimming hardware on ATM card readers and overlay "
                "PIN pads at the bank's 18 ATMs across Nairobi and Mombasa, leading to "
                "fraudulent card cloning and customer financial losses."
            ),
            threat="Physical / card fraud",
            impact="High", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Deploying anti-skimming bezels on all ATMs by end of Q2 2026. "
                "Weekly ATM inspection programme rolled out to branch managers. "
                "Geo-velocity fraud rules activated on card issuing system."
            ),
            owner="Head of Operations",
            status="Open",
            tags=["atm", "card-fraud", "physical-security"],
            review_date=date(2026, 6, 30),
        ),
        # ---- R-04 ----
        _risk(
            title="Ransomware attack targeting HQ Windows domain",
            description=(
                "A spear-phishing email targeted at finance staff delivers a ransomware payload "
                "that propagates via SMB across the Windows domain, encrypting FLEXCUBE "
                "application servers and document management systems."
            ),
            threat="Ransomware / spear-phishing",
            impact="Critical", likelihood="Unlikely",
            treatment="Mitigate",
            treatment_notes=(
                "Deployed CrowdStrike Falcon EDR on all endpoints. Network segmentation between "
                "SWIFT, FLEXCUBE, and office networks completed. Immutable offsite backups to "
                "Rackspace Nairobi tested monthly. CBK cyber incident notification template prepared."
            ),
            owner="Chief Information Security Officer",
            status="Open",
            tags=["ransomware", "endpoint", "business-continuity"],
        ),
        # ---- R-05 ----
        _risk(
            title="Insider fraud — privileged staff executing unauthorised RTGS transfers",
            description=(
                "A teller or back-office officer with FLEXCUBE Payments module access "
                "initiates unauthorised high-value RTGS payments to a mule account, "
                "exploiting weak four-eye authorisation controls."
            ),
            threat="Insider / financial crime",
            impact="Critical", likelihood="Unlikely",
            treatment="Mitigate",
            treatment_notes=(
                "Mandatory dual-authorisation for all RTGS >KES 500,000 enforced at application layer. "
                "SIEM correlation rule alerts on payments approved by the same user branch. "
                "Annual rotation of payments module privileges."
            ),
            owner="Head of Compliance",
            status="In Treatment",
            tags=["insider-threat", "rtgs", "fraud", "access-control"],
            review_date=date(2026, 7, 15),
            residual_impact="High", residual_likelihood="Rare",
        ),
        # ---- R-06 ----
        _risk(
            title="Kenya Data Protection Act — failure to respond to data subject requests",
            description=(
                "Savanna Bank fails to fulfil data subject access requests (DSARs) or erasure "
                "requests within the 30-day deadline prescribed by the Kenya Data Protection "
                "Act 2019, risking enforcement action by the Office of the Data Protection "
                "Commissioner (ODPC) and reputational damage."
            ),
            threat="Regulatory non-compliance",
            impact="Medium", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Implemented a DSAR ticketing workflow in Jira Service Management with "
                "automated SLA escalation at Day 20. DPO appointed; ODPC registration renewed."
            ),
            owner="Data Protection Officer",
            status="In Treatment",
            tags=["gdpr", "kdpa", "privacy", "compliance"],
            review_date=date(2026, 9, 1),
        ),
        # ---- R-07 ----
        _risk(
            title="CBK on-site IT examination — unresolved prior findings",
            description=(
                "The Central Bank of Kenya's Bank Supervision Department raised 6 IT governance "
                "findings in the 2024 on-site examination. Failure to remediate before the "
                "next examination (scheduled Q3 2026) may result in supervisory directions "
                "or public censure."
            ),
            threat="Regulatory",
            impact="High", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Remediation tracker maintained by CISO. 4 of 6 findings closed. "
                "Remaining 2 (patch management SLA evidence, board IT risk reporting) "
                "targeted for closure by June 2026."
            ),
            owner="Chief Information Security Officer",
            status="In Treatment",
            tags=["cbk", "regulatory", "governance"],
            review_date=date(2026, 6, 30),
        ),
        # ---- R-08 ----
        _risk(
            title="Mobile banking app credential stuffing — customer account takeover",
            description=(
                "Automated bots attempt to access Savanna Bank mobile app accounts using "
                "credential lists obtained from third-party breaches, leading to account "
                "takeover fraud and SIM-swap-assisted OTP bypass."
            ),
            threat="Account takeover / credential stuffing",
            impact="High", likelihood="Likely",
            treatment="Mitigate",
            treatment_notes=(
                "CAPTCHA and device fingerprinting added to login. Step-up authentication "
                "(biometric or OTP) required for transactions >KES 10,000. "
                "Rate limiting at API gateway: max 5 failed logins per 60s per IP."
            ),
            owner="Head of Digital Banking",
            status="In Treatment",
            tags=["mobile-banking", "account-takeover", "authentication"],
            review_date=date(2026, 7, 1),
            residual_impact="Medium", residual_likelihood="Unlikely",
        ),
        # ---- R-09 ----
        _risk(
            title="SWIFT Customer Security Programme — control gap identified",
            description=(
                "Savanna Bank's self-attestation for the SWIFT CSP 2026 mandatory controls "
                "identified a gap in Control 1.2 (Privileged Account Management): shared "
                "admin credentials still used for the SWIFT Alliance Gateway. "
                "Non-compliance may trigger correspondent bank de-risking."
            ),
            threat="SWIFT network security / de-risking",
            impact="Critical", likelihood="Unlikely",
            treatment="Mitigate",
            treatment_notes=(
                "Privileged Access Workstation (PAW) deployment underway for SWIFT Gateway. "
                "Individual named accounts replacing shared admin by 30 June 2026. "
                "External SWIFT CSP audit scheduled for July 2026."
            ),
            owner="Chief Information Security Officer",
            status="In Treatment",
            tags=["swift", "csp", "correspondent-banking", "access-control"],
            review_date=date(2026, 6, 30),
        ),
        # ---- R-10 ----
        _risk(
            title="Third-party data centre power failure — extended outage",
            description=(
                "Savanna Bank's primary data centre (co-location in Nairobi CBD) experiences "
                "an extended mains power failure beyond UPS and generator autonomy (>8 hours), "
                "causing a full production outage and exceeding the 4-hour RTO."
            ),
            threat="Physical / infrastructure",
            impact="High", likelihood="Rare",
            treatment="Mitigate",
            treatment_notes=(
                "DR site in Upper Hill activated annually. Added second 100kVA generator at "
                "primary DC. Fuel contract with immediate-response SLA signed. Closed — "
                "residual risk accepted post-controls."
            ),
            owner="Chief Technology Officer",
            status="Closed",
            tags=["data-centre", "availability", "business-continuity"],
        ),
    ]

    for r in risks:
        session.add(r)
    await session.flush()

    # ------------------------------------------------------------------
    # 2. Control mappings — link risks to ISO 27001 controls
    # ------------------------------------------------------------------
    iso = (await session.execute(
        select(Framework).where(Framework.slug == "iso27001")
    )).scalar_one_or_none()

    if iso:
        controls_result = await session.execute(
            select(Control).where(Control.framework_id == iso.id)
        )
        controls_by_ref = {c.ref: c for c in controls_result.scalars().all()}

        # risk index → ISO 27001:2022 control refs
        mappings = {
            0: ["8.24", "8.25"],    # M-Pesa API → crypto/secure dev
            1: ["8.14", "8.6"],     # FLEXCUBE outage → redundancy, capacity
            2: ["7.4", "8.21"],     # ATM skimming → physical monitoring, network security
            3: ["8.7", "8.12"],     # Ransomware → anti-malware, data leakage
            4: ["5.18", "8.2"],     # Insider fraud → access rights, privileged access
            5: ["5.34"],            # KDPA → privacy
            6: ["5.35"],            # CBK examination → legal compliance
            7: ["8.21", "8.22"],    # Mobile banking → network security, web filtering
            8: ["5.18", "8.2"],     # SWIFT CSP → privileged access
        }
        for risk_idx, refs in mappings.items():
            for ref in refs:
                ctrl = controls_by_ref.get(ref)
                if ctrl:
                    session.add(RiskControl(risk_id=risks[risk_idx].id, control_id=ctrl.id))

    await session.flush()

    # ------------------------------------------------------------------
    # 3. Evidence
    # ------------------------------------------------------------------
    evidence_items = [
        _evidence(
            title="CBK IT Risk On-Site Examination Report 2025",
            description=(
                "Central Bank of Kenya Bank Supervision Department findings from the Q3 2025 "
                "on-site IT examination. 6 findings raised; 4 closed, 2 in remediation."
            ),
            file_name="cbk_it_examination_report_2025.pdf",
            file_size=3_241_984,
            mime_type="application/pdf",
            expiry_date=date(2027, 9, 30),
        ),
        _evidence(
            title="PCI DSS v4.0 Compliance Certificate — Acquirer",
            description=(
                "Acquirer-level PCI DSS v4.0 compliance certificate issued by Sysnet Global "
                "Solutions following QSA audit of card payment processing environment."
            ),
            file_name="pci_dss_v4_certificate_2025.pdf",
            file_size=418_816,
            mime_type="application/pdf",
            expiry_date=date(2026, 11, 30),
        ),
        _evidence(
            title="Safaricom M-Pesa Daraja API Security Assessment Report",
            description=(
                "Internal security assessment of the M-Pesa Daraja API integration layer, "
                "covering credential management, webhook signature validation, and float "
                "account monitoring controls."
            ),
            file_name="mpesa_daraja_security_assessment_2026.pdf",
            file_size=1_892_352,
            mime_type="application/pdf",
        ),
        _evidence(
            title="ODPC Data Controller Registration Certificate",
            description=(
                "Office of the Data Protection Commissioner (Kenya) registration certificate "
                "confirming Savanna Commercial Bank's registration as a data controller "
                "under the Kenya Data Protection Act 2019."
            ),
            file_name="odpc_registration_cert_2025.pdf",
            file_size=287_744,
            mime_type="application/pdf",
            # Expiring within 30 days of today (2026-05-26) → status = Expiring
            expiry_date=date(2026, 6, 14),
        ),
        _evidence(
            title="Business Continuity & DR Test Results — Q4 2025",
            description=(
                "Documentation of the Q4 2025 full DR switchover test to Upper Hill secondary "
                "data centre. RTO achieved: 3h 42m (target: 4h). RPO: 18 minutes (target: 1h)."
            ),
            file_name="bcp_dr_test_results_q4_2025.docx",
            file_size=856_064,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        _evidence(
            title="ISO 27001:2022 Stage 2 Certification Audit Report",
            description=(
                "BSI Group Stage 2 certification audit report. Certificate awarded October 2025. "
                "2 minor non-conformances raised (patch cadence evidence, supplier review frequency); "
                "both closed at surveillance audit."
            ),
            file_name="iso27001_certification_audit_2025.pdf",
            file_size=4_096_000,
            mime_type="application/pdf",
            expiry_date=date(2028, 10, 15),
        ),
        _evidence(
            title="SWIFT CSP Self-Attestation 2024 — KE-SAVB-XXX",
            description=(
                "SWIFT Customer Security Programme (CSP) self-attestation submitted for "
                "FY2024 mandatory controls. Identified gap in Control 1.2 (PAM) — "
                "remediation in progress for 2025 attestation."
            ),
            file_name="swift_csp_attestation_2024.pdf",
            file_size=621_568,
            mime_type="application/pdf",
            # Already expired → status = Expired
            expiry_date=date(2025, 12, 31),
        ),
        _evidence(
            title="CrowdStrike Falcon — EDR Deployment Coverage Report",
            description=(
                "Report confirming CrowdStrike Falcon Prevent deployed on 98.4% of managed "
                "endpoints (243/247 devices). 4 legacy ATM management servers pending "
                "OS upgrade before agent installation."
            ),
            file_name="crowdstrike_coverage_report_may2026.xlsx",
            file_size=94_208,
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    ]

    for ev in evidence_items:
        session.add(ev)

    # ------------------------------------------------------------------
    # 4. Vendors
    # ------------------------------------------------------------------
    vendors_data = [
        dict(
            name="Safaricom PLC (M-Pesa)",
            description=(
                "Primary mobile money integration via Daraja API. Processes all M-Pesa "
                "P2B, B2C, and STK Push transactions. Float held in Safaricom trust account."
            ),
            category="Mobile Money / Payments",
            website="https://developer.safaricom.co.ke",
            tier=1, status="Active",
            contact_name="Safaricom Enterprise Relationship Manager",
            contact_email="enterprise@safaricom.co.ke",
            contract_start=date(2019, 3, 1), contract_end=date(2027, 2, 28),
            score=87.6,
        ),
        dict(
            name="Oracle Financial Services (FLEXCUBE)",
            description=(
                "Core Banking System — Oracle FLEXCUBE Universal Banking v14.5. "
                "Hosts all customer accounts, loans, deposits, and RTGS/EFT payment origination."
            ),
            category="Core Banking System",
            website="https://www.oracle.com/financialservices",
            tier=1, status="Active",
            contact_name="Oracle Premier Support",
            contact_email="flexcube.support@oracle.com",
            contract_start=date(2016, 6, 1), contract_end=date(2028, 5, 31),
            score=91.3,
        ),
        dict(
            name="Craft Silicon Limited",
            description=(
                "Mobile and internet banking platform (Elma). Provides the customer-facing "
                "Android, iOS, and web banking applications integrated with FLEXCUBE via REST APIs."
            ),
            category="Digital Banking Platform",
            website="https://www.craftsilicon.com",
            tier=2, status="Active",
            contact_name="Craft Silicon Account Manager",
            contact_email="banking@craftsilicon.com",
            contract_start=date(2020, 1, 1), contract_end=date(2026, 12, 31),
            score=68.9,
        ),
        dict(
            name="Microsoft Azure (East Africa)",
            description=(
                "Cloud platform used for dev/test workloads, Azure AD for identity federation, "
                "and Sentinel SIEM ingesting FLEXCUBE and M-Pesa API logs."
            ),
            category="Cloud Infrastructure",
            website="https://azure.microsoft.com",
            tier=2, status="Active",
            contact_name="Microsoft Banking & Capital Markets Team",
            contact_email="azurebanking@microsoft.com",
            contract_start=date(2022, 7, 1), contract_end=date(2027, 6, 30),
            score=79.4,
        ),
        dict(
            name="InfoMark Kenya Limited",
            description=(
                "On-site IT hardware maintenance and ATM first-line support across Nairobi "
                "and Mombasa branch network. Access to ATM internals and branch server rooms."
            ),
            category="IT Support & Maintenance",
            website="https://infomark.co.ke",
            tier=3, status="Under Review",
            contact_name="InfoMark Operations Manager",
            contact_email="ops@infomark.co.ke",
            contract_start=date(2021, 4, 1), contract_end=date(2026, 3, 31),
            score=44.8,
        ),
    ]

    vendor_objs = []
    for vd in vendors_data:
        score = vd.pop("score")
        vendor = Vendor(id=uuid.uuid4(), **vd)
        session.add(vendor)
        vendor_objs.append((vendor, score))

    await session.flush()

    now_utc = datetime.now(timezone.utc)
    for vendor, score in vendor_objs:
        session.add(VendorAssessment(
            id=uuid.uuid4(),
            vendor_id=vendor.id,
            status="Complete",
            overall_score=score,
            updated_at=now_utc,
        ))

    # ------------------------------------------------------------------
    # 5. Audit Plan — CBK IT Readiness Assessment FY2026
    # ------------------------------------------------------------------
    plan = AuditPlan(
        id=uuid.uuid4(),
        title="CBK IT Risk & Governance Readiness Assessment — FY2026",
        scope=(
            "In-scope systems: Oracle FLEXCUBE core banking, M-Pesa Daraja API integration, "
            "Craft Silicon mobile/internet banking, SWIFT Alliance Gateway, Azure SIEM. "
            "CBK Prudential Guidelines on IT Risk (2023) and ISO 27001:2022 control objectives."
        ),
        status="Active",
        audit_start=date(2026, 5, 1),
        audit_end=date(2026, 7, 31),
    )
    session.add(plan)
    await session.flush()

    items = [
        AuditItem(plan_id=plan.id, test_result="Pass",
                  description="Verify that privileged FLEXCUBE accounts are individually named and use MFA — confirm no shared admin credentials exist."),
        AuditItem(plan_id=plan.id, test_result="Pass",
                  description="Review RTGS dual-authorisation audit log for the last 30 days — confirm no single-authorised high-value payments processed."),
        AuditItem(plan_id=plan.id, test_result="Fail",
                  description="Confirm critical and high vulnerability remediation SLA (7 days critical, 30 days high) — sample last three vulnerability scan reports.",
                  notes="April scan: CVE-2026-11423 (CVSS 9.1, Windows Server 2019) open for 22 days. SLA breach confirmed."),
        AuditItem(plan_id=plan.id, test_result="Pass",
                  description="Review M-Pesa Daraja API credentials storage — confirm no plaintext secrets in source code repositories or CI/CD environment variables."),
        AuditItem(plan_id=plan.id, test_result="Exception",
                  description="Confirm DR switchover test conducted within last 12 months and RTO/RPO targets met.",
                  notes="DR test completed Q4 2025 (RTO 3h42m vs 4h target — PASS). Documentation not yet formally signed off by CTO. Accepted as exception pending sign-off by 30 June."),
        AuditItem(plan_id=plan.id, test_result="Not Tested",
                  description="Review SWIFT CSP 2025 mandatory self-attestation — confirm all mandatory controls evidenced and attestation submitted to SWIFT portal."),
        AuditItem(plan_id=plan.id, test_result="Pass",
                  description="Verify ODPC data controller registration is current and Data Protection Impact Assessments (DPIAs) exist for high-risk processing activities."),
        AuditItem(plan_id=plan.id, test_result="Fail",
                  description="Review ATM anti-skimming controls — confirm anti-skimming bezels installed on all 18 ATMs and weekly inspection logs current.",
                  notes="6 of 18 ATMs still awaiting bezel installation (Mombasa branch — 3, Karen branch — 3). Inspection logs missing for 2 weeks at Westlands branch."),
    ]
    for item in items:
        session.add(item)

    findings = [
        AuditFinding(
            plan_id=plan.id,
            title="Critical vulnerability unpatched beyond CBK/policy SLA",
            description=(
                "CVE-2026-11423 (CVSS 9.1) affecting Windows Server 2019 — used by the FLEXCUBE "
                "application server — has been open for 22 days without a patch applied, exceeding "
                "the bank's Vulnerability Management Policy SLA of 7 days for Critical findings. "
                "This also breaches the CBK IT Risk Guideline requirement for timely patch management."
            ),
            severity="High",
            status="Open",
            owner="Head of Infrastructure",
            due_date=date(2026, 6, 10),
        ),
        AuditFinding(
            plan_id=plan.id,
            title="ATM anti-skimming bezel deployment incomplete",
            description=(
                "6 of 18 ATMs in the branch network (Mombasa branch: 3 units, Karen branch: 3 units) "
                "have not yet had anti-skimming bezels installed despite the June 2026 board-approved "
                "deadline. Additionally, weekly physical inspection logs are incomplete for "
                "Westlands branch (2 consecutive weeks missing)."
            ),
            severity="High",
            status="Open",
            owner="Head of Operations",
            due_date=date(2026, 6, 30),
        ),
        AuditFinding(
            plan_id=plan.id,
            title="SWIFT CSP 2025 attestation not yet submitted",
            description=(
                "The SWIFT Customer Security Programme mandatory self-attestation for 2025 "
                "has not been submitted to the SWIFT portal. The submission deadline was "
                "31 December 2025. Failure to attest risks sanctions from correspondent banks "
                "and SWIFT de-listing."
            ),
            severity="Critical",
            status="Open",
            owner="Chief Information Security Officer",
            due_date=date(2026, 6, 1),
        ),
        AuditFinding(
            plan_id=plan.id,
            title="DR test documentation lacks CTO sign-off",
            description=(
                "Q4 2025 DR test results are complete and RTO/RPO targets were met, however "
                "the formal test report has not been signed off by the CTO as required by "
                "the BCP policy, preventing the finding from being closed."
            ),
            severity="Low",
            status="Remediated",
            owner="Chief Technology Officer",
            due_date=date(2026, 5, 31),
        ),
    ]
    for finding in findings:
        session.add(finding)

    await session.commit()
    logger.info("Savanna Commercial Bank demo data seeded successfully")
