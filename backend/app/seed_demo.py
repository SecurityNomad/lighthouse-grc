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
from app.models.soa import ControlApplicability

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


def _soa(control_id, applicable, status, justification, owner, reviewed=None):
    return ControlApplicability(
        id=uuid.uuid4(),
        control_id=control_id,
        applicable=applicable,
        implementation_status=status,
        justification=justification,
        owner=owner,
        last_reviewed=reviewed or date(2026, 4, 30),
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
        # ---- R-11 ----
        _risk(
            title="Unpatched critical vulnerabilities on internet-facing infrastructure",
            description=(
                "Critical and high-severity vulnerabilities on the internet-facing web "
                "application firewall, VPN concentrator, and FLEXCUBE application servers "
                "remain unpatched beyond the Vulnerability Management Policy SLA of 7 days "
                "(Critical) and 30 days (High), exposing the bank to remote exploitation."
            ),
            threat="Vulnerability exploitation",
            impact="Critical", likelihood="Likely",
            treatment="Mitigate",
            treatment_notes=(
                "Qualys authenticated scanning extended to all external assets. "
                "Monthly patch window formalised with CAB approval. Emergency patch "
                "procedure documented for CVSS >9.0. Tracked as audit finding AF-01."
            ),
            owner="Head of Infrastructure",
            status="In Treatment",
            tags=["vulnerability-management", "patching", "cbk"],
            review_date=date(2026, 6, 10),
            residual_impact="High", residual_likelihood="Unlikely",
        ),
        # ---- R-12 ----
        _risk(
            title="Legacy branch WAN links carrying unencrypted internal traffic",
            description=(
                "Three upcountry branches (Nakuru, Eldoret, Kisumu) connect to the core "
                "network over legacy leased lines without IPSec encryption, exposing "
                "customer data and FLEXCUBE session traffic to interception on the "
                "carrier network."
            ),
            threat="Data interception / weak cryptography",
            impact="High", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "IPSec tunnels being deployed across all branch links by Liquid Telecom. "
                "12 of 15 branches migrated. Remaining 3 scheduled for Q3 2026."
            ),
            owner="Head of Infrastructure",
            status="In Treatment",
            tags=["network", "encryption", "branch"],
            review_date=date(2026, 9, 30),
            residual_impact="Medium", residual_likelihood="Rare",
        ),
        # ---- R-13 ----
        _risk(
            title="Azure storage misconfiguration exposing SIEM log archives",
            description=(
                "Misconfigured Azure blob storage containers holding archived Sentinel SIEM "
                "logs and FLEXCUBE transaction extracts could be made publicly accessible "
                "through an over-permissive access policy or an accidental anonymous-access "
                "setting during routine administration."
            ),
            threat="Cloud misconfiguration",
            impact="High", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Azure Policy deny-rules applied to block anonymous blob access tenant-wide. "
                "Microsoft Defender for Cloud secure-score monitoring enabled with weekly "
                "review by the security operations team."
            ),
            owner="Chief Information Security Officer",
            status="In Treatment",
            tags=["cloud", "azure", "misconfiguration", "data-exposure"],
            review_date=date(2026, 8, 15),
            residual_impact="Medium", residual_likelihood="Unlikely",
        ),
        # ---- R-14 ----
        _risk(
            title="Backup restoration failure — untested FLEXCUBE recovery path",
            description=(
                "Nightly FLEXCUBE database backups complete successfully but full restoration "
                "has not been tested end to end since 2024. An undetected corruption or an "
                "incomplete transaction-log chain could prevent recovery within the 4-hour RTO "
                "following a ransomware event or storage failure."
            ),
            threat="Data loss / recovery failure",
            impact="Critical", likelihood="Unlikely",
            treatment="Mitigate",
            treatment_notes=(
                "Quarterly restore-to-isolated-environment test added to the BCP calendar. "
                "First test completed May 2026: full restore achieved in 2h 51m. "
                "Immutable backup copies retained at Rackspace Nairobi."
            ),
            owner="Chief Technology Officer",
            status="In Treatment",
            tags=["backup", "recovery", "business-continuity", "ransomware"],
            review_date=date(2026, 8, 31),
            residual_impact="High", residual_likelihood="Rare",
        ),
        # ---- R-15 ----
        _risk(
            title="SIEM coverage gaps — ATM and branch systems not forwarding logs",
            description=(
                "Azure Sentinel ingests logs from FLEXCUBE, the M-Pesa integration layer, and "
                "Azure AD, but ATM controllers and branch file servers do not forward events. "
                "Security incidents originating at branch level may go undetected, and the "
                "gap undermines CBK incident-reporting obligations."
            ),
            threat="Detection gap / monitoring",
            impact="Medium", likelihood="Likely",
            treatment="Mitigate",
            treatment_notes=(
                "Syslog forwarding agents being rolled out to ATM controllers. "
                "Branch file server onboarding scheduled after the Q3 network refresh."
            ),
            owner="Chief Information Security Officer",
            status="Open",
            tags=["siem", "monitoring", "detection", "atm"],
            review_date=date(2026, 10, 31),
        ),
        # ---- R-16 ----
        _risk(
            title="Supplier concentration — single vendor for all digital banking channels",
            description=(
                "Craft Silicon Limited supplies the mobile app, internet banking portal, and "
                "the integration middleware to FLEXCUBE. Vendor failure, contract dispute, or "
                "a security incident at the supplier would simultaneously remove every "
                "digital channel, with no substitutable alternative in place."
            ),
            threat="Supplier concentration / availability",
            impact="Critical", likelihood="Unlikely",
            treatment="Mitigate",
            treatment_notes=(
                "Source-code escrow agreement executed with a Nairobi escrow agent. "
                "Exit plan drafted covering data extraction and a 6-month transition. "
                "Second-source evaluation added to the FY2027 technology roadmap."
            ),
            owner="Chief Technology Officer",
            status="In Treatment",
            tags=["vendor", "concentration", "digital-banking", "tprm"],
            review_date=date(2026, 12, 31),
            residual_impact="High", residual_likelihood="Rare",
        ),
        # ---- R-17 ----
        _risk(
            title="Unvetted subcontractor access to ATM internals and branch server rooms",
            description=(
                "InfoMark Kenya Limited subcontracts ATM first-line maintenance to third-party "
                "engineers who have not been background-screened by the bank and are not named "
                "in the contract. These engineers obtain physical access to ATM safes, card "
                "readers, and branch server rooms."
            ),
            threat="Third-party physical access",
            impact="High", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Contract variation requiring named, screened engineers issued to InfoMark. "
                "Vendor status moved to Under Review pending evidence of screening. "
                "Escorted-access policy enforced for all branch server rooms from June 2026."
            ),
            owner="Head of Operations",
            status="In Treatment",
            tags=["vendor", "physical-security", "atm", "tprm"],
            review_date=date(2026, 7, 31),
        ),
        # ---- R-18 ----
        _risk(
            title="Fourth-party risk — undisclosed sub-processors in the digital banking chain",
            description=(
                "Craft Silicon uses undisclosed cloud sub-processors for push-notification "
                "delivery and analytics on the mobile banking app. Customer identifiers may be "
                "transferred outside Kenya without an ODPC-compliant transfer mechanism or "
                "the bank's knowledge."
            ),
            threat="Fourth-party / data transfer",
            impact="Medium", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Sub-processor disclosure clause added at contract renewal. "
                "DPIA updated to cover cross-border transfers. Awaiting a full "
                "sub-processor register from the supplier."
            ),
            owner="Data Protection Officer",
            status="Open",
            tags=["vendor", "fourth-party", "privacy", "kdpa"],
            review_date=date(2026, 9, 30),
        ),
        # ---- R-19 ----
        _risk(
            title="Vendor contracts lapsing without security review or renewal",
            description=(
                "Several supplier contracts, including InfoMark Kenya (expired 31 March 2026) "
                "and Craft Silicon (expiring 31 December 2026), have reached or are approaching "
                "expiry without a documented security review, leaving services delivered "
                "without current contractual security obligations."
            ),
            threat="Contract lapse / governance",
            impact="Medium", likelihood="Likely",
            treatment="Mitigate",
            treatment_notes=(
                "Contract register migrated into the Lighthouse TPRM module with renewal "
                "alerts at 90 days. Procurement now requires a security sign-off before "
                "any renewal is executed."
            ),
            owner="Head of Compliance",
            status="In Treatment",
            tags=["vendor", "contract", "governance", "tprm"],
            review_date=date(2026, 6, 30),
            residual_impact="Low", residual_likelihood="Unlikely",
        ),
        # ---- R-20 ----
        _risk(
            title="Agency banking agent fraud — unauthorised customer transactions",
            description=(
                "Savanna Bank agency banking agents operating in retail outlets process "
                "deposits and withdrawals on behalf of customers. Agents may under-record "
                "deposits, retain customer cards or PINs, or process transactions without "
                "customer authorisation."
            ),
            threat="Agent fraud / financial crime",
            impact="Medium", likelihood="Likely",
            treatment="Mitigate",
            treatment_notes=(
                "SMS confirmation to customers on every agent transaction. "
                "Agent transaction limits reduced. Mystery-shopper programme launched "
                "across the agent network in Q2 2026."
            ),
            owner="Head of Operations",
            status="In Treatment",
            tags=["agency-banking", "fraud", "operations"],
            review_date=date(2026, 8, 31),
            residual_impact="Low", residual_likelihood="Possible",
        ),
        # ---- R-21 ----
        _risk(
            title="Tailgating and uncontrolled access to branch server rooms",
            description=(
                "Branch server rooms are secured by shared mechanical keys held at the branch "
                "manager's desk rather than by badge-controlled access. There is no access log, "
                "so entry by cleaners, contractors, or unauthorised staff cannot be evidenced "
                "or reconstructed after an incident."
            ),
            threat="Physical access control",
            impact="Medium", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Badge readers installed at 9 of 15 branches. Remaining 6 scheduled by "
                "Q4 2026. Interim key-register sign-out sheet mandated at all branches."
            ),
            owner="Head of Operations",
            status="Open",
            tags=["physical-security", "branch", "access-control"],
            review_date=date(2026, 11, 30),
        ),
        # ---- R-22 ----
        _risk(
            title="Key person dependency — single FLEXCUBE database administrator",
            description=(
                "One database administrator holds the operational knowledge and the privileged "
                "credentials required to administer the FLEXCUBE Oracle estate. Absence, "
                "resignation, or incapacity would leave the bank unable to perform recovery, "
                "patching, or month-end processing."
            ),
            threat="Key person / operational resilience",
            impact="High", likelihood="Possible",
            treatment="Mitigate",
            treatment_notes=(
                "Second DBA recruited, starting July 2026. Runbooks for month-end and "
                "recovery procedures documented and peer-reviewed. Break-glass credentials "
                "held in escrow with the CTO."
            ),
            owner="Chief Technology Officer",
            status="In Treatment",
            tags=["key-person", "resilience", "core-banking"],
            review_date=date(2026, 7, 31),
            residual_impact="Medium", residual_likelihood="Unlikely",
        ),
        # ---- R-23 ----
        _risk(
            title="EFT and cheque clearing reconciliation breaks",
            description=(
                "Daily reconciliation between the FLEXCUBE general ledger and the Kenya "
                "Bankers Association clearing house occasionally shows unexplained breaks "
                "that are cleared manually. Manual adjustment without independent review "
                "could mask error or misappropriation."
            ),
            threat="Reconciliation / financial control",
            impact="Medium", likelihood="Possible",
            treatment="Accept",
            treatment_notes=(
                "Break volumes are low (average 3 per month, all under KES 20,000) and are "
                "reviewed by Finance within 48 hours. Automated reconciliation tooling "
                "assessed as disproportionate to the exposure. Accepted by ALCO, "
                "reviewed annually."
            ),
            owner="Head of Finance",
            status="Accepted",
            tags=["reconciliation", "finance", "operations"],
            review_date=date(2027, 3, 31),
        ),
        # ---- R-24 ----
        _risk(
            title="AML transaction monitoring — excessive false positives masking true alerts",
            description=(
                "The AML transaction monitoring system generates a high volume of false-positive "
                "alerts because thresholds have not been tuned since implementation. Analyst "
                "fatigue risks a genuine suspicious transaction being closed without "
                "investigation, breaching reporting obligations to the Financial Reporting Centre."
            ),
            threat="Financial crime / regulatory",
            impact="High", likelihood="Likely",
            treatment="Mitigate",
            treatment_notes=(
                "Threshold tuning exercise with the vendor completed for cash-deposit and "
                "M-Pesa typologies, reducing alert volume by 41%. Quarterly model review "
                "added to the compliance calendar."
            ),
            owner="Head of Compliance",
            status="In Treatment",
            tags=["aml", "financial-crime", "regulatory", "monitoring"],
            review_date=date(2026, 9, 30),
            residual_impact="Medium", residual_likelihood="Possible",
        ),
        # ---- R-25 ----
        _risk(
            title="Board IT risk reporting insufficient for CBK governance expectations",
            description=(
                "IT and cyber risk is reported to the Board Risk Committee as a narrative "
                "update without quantified metrics, trend data, or risk appetite thresholds. "
                "This was raised in the 2024 CBK on-site examination and remains one of the "
                "two open findings from that examination."
            ),
            threat="Governance / regulatory",
            impact="Medium", likelihood="Likely",
            treatment="Mitigate",
            treatment_notes=(
                "Quarterly Board IT risk dashboard designed, drawing metrics directly from "
                "the Lighthouse risk register and control coverage reporting. "
                "First formal submission tabled at the June 2026 Board Risk Committee."
            ),
            owner="Chief Information Security Officer",
            status="In Treatment",
            tags=["governance", "cbk", "board", "reporting"],
            review_date=date(2026, 6, 30),
            residual_impact="Low", residual_likelihood="Unlikely",
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
            9: ["7.11", "8.14"],    # DC power failure → utilities, redundancy
            10: ["8.8", "8.32"],    # Unpatched vulns → technical vulns, change mgmt
            11: ["8.24", "8.21"],   # Unencrypted WAN → cryptography, network services
            12: ["5.23", "8.9"],    # Azure misconfig → cloud services, configuration mgmt
            13: ["8.13", "5.29"],   # Backup restore → backup, disruption readiness
            14: ["8.15", "8.16"],   # SIEM gaps → logging, monitoring
            15: ["5.21", "5.30"],   # Supplier concentration → ICT supply chain, BC readiness
            16: ["5.19", "7.2"],    # Subcontractor access → supplier relationships, physical entry
            17: ["5.22", "5.34"],   # Fourth-party → supplier monitoring, privacy
            18: ["5.20", "5.22"],   # Contract lapse → supplier agreements, supplier monitoring
            19: ["5.19", "8.16"],   # Agency fraud → supplier relationships, monitoring
            20: ["7.2", "7.3"],     # Tailgating → physical entry, securing offices
            21: ["5.2", "5.30"],    # Key person → roles/responsibilities, ICT BC readiness
            22: ["5.4", "5.36"],    # Reconciliation → management responsibilities, compliance
            23: ["5.36", "8.16"],   # AML monitoring → compliance, monitoring
            24: ["5.1", "5.4"],     # Board reporting → policies, management responsibilities
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
        dict(
            name="Interswitch East Africa Limited",
            description=(
                "Card switching and payment processing. Routes all Visa and Mastercard "
                "authorisations for the bank's issued cards and ATM acquiring traffic."
            ),
            category="Card Switching / Payments",
            website="https://www.interswitchgroup.com",
            tier=1, status="Active",
            contact_name="Interswitch Service Delivery Manager",
            contact_email="support@interswitchgroup.com",
            contract_start=date(2018, 9, 1), contract_end=date(2027, 8, 31),
            score=84.2,
        ),
        dict(
            name="Thales DIS (HSM & Card Personalisation)",
            description=(
                "Hardware security modules protecting PIN blocks and card cryptographic keys, "
                "plus card personalisation bureau services for debit card issuance."
            ),
            category="Cryptographic Hardware",
            website="https://cpl.thalesgroup.com",
            tier=1, status="Active",
            contact_name="Thales Financial Services Team",
            contact_email="banking.support@thalesgroup.com",
            contract_start=date(2017, 11, 1), contract_end=date(2027, 10, 31),
            score=93.5,
        ),
        dict(
            name="Kenswitch Limited",
            description=(
                "Domestic ATM interswitching network enabling Savanna cardholders to "
                "transact at other member banks' ATMs across Kenya."
            ),
            category="ATM Network / Interswitching",
            website="https://www.kenswitch.com",
            tier=2, status="Active",
            contact_name="Kenswitch Operations Desk",
            contact_email="operations@kenswitch.com",
            contract_start=date(2015, 5, 1), contract_end=date(2026, 12, 31),
            score=76.1,
        ),
        dict(
            name="CrowdStrike Inc.",
            description=(
                "Falcon Prevent endpoint detection and response deployed across managed "
                "endpoints and FLEXCUBE application servers. Cloud-delivered, US-hosted tenancy."
            ),
            category="Endpoint Security",
            website="https://www.crowdstrike.com",
            tier=2, status="Active",
            contact_name="CrowdStrike EMEA Account Team",
            contact_email="emea-support@crowdstrike.com",
            contract_start=date(2024, 2, 1), contract_end=date(2027, 1, 31),
            score=89.7,
        ),
        dict(
            name="Rackspace Technology (Nairobi)",
            description=(
                "Offsite immutable backup repository for FLEXCUBE database backups and "
                "document management archives. Contracted for 30-day immutability."
            ),
            category="Backup & Storage",
            website="https://www.rackspace.com",
            tier=2, status="Active",
            contact_name="Rackspace Service Delivery",
            contact_email="support@rackspace.co.ke",
            contract_start=date(2023, 1, 1), contract_end=date(2026, 12, 31),
            score=81.0,
        ),
        dict(
            name="Liquid Intelligent Technologies Kenya",
            description=(
                "Branch WAN connectivity and primary internet transit. Provides leased lines "
                "to all 15 branches and the IPSec overlay currently being deployed."
            ),
            category="Network & Connectivity",
            website="https://liquid.tech",
            tier=2, status="Active",
            contact_name="Liquid Enterprise Account Manager",
            contact_email="enterprise.ke@liquid.tech",
            contract_start=date(2020, 10, 1), contract_end=date(2026, 9, 30),
            score=71.5,
        ),
        dict(
            name="Sysnet Global Solutions",
            description=(
                "Qualified Security Assessor (QSA) for the annual PCI DSS v4.0 assessment "
                "of the card payment processing environment."
            ),
            category="Assurance / Audit",
            website="https://www.sysnetgs.com",
            tier=3, status="Active",
            contact_name="Sysnet Lead QSA",
            contact_email="qsa@sysnetgs.com",
            contract_start=date(2022, 1, 1), contract_end=date(2026, 12, 31),
            score=88.4,
        ),
        dict(
            name="BSI Group Kenya",
            description=(
                "ISO/IEC 27001:2022 certification body. Conducted the Stage 1 and Stage 2 "
                "certification audits and performs annual surveillance audits."
            ),
            category="Certification Body",
            website="https://www.bsigroup.com",
            tier=3, status="Active",
            contact_name="BSI Lead Auditor",
            contact_email="certification.ke@bsigroup.com",
            contract_start=date(2025, 3, 1), contract_end=date(2028, 2, 29),
            score=90.2,
        ),
        dict(
            name="Atlassian Corporation",
            description=(
                "Jira Service Management hosting the DSAR ticketing workflow, change "
                "management records, and IT service desk. Cloud-hosted outside Kenya."
            ),
            category="SaaS / Workflow",
            website="https://www.atlassian.com",
            tier=3, status="Active",
            contact_name="Atlassian Cloud Support",
            contact_email="support@atlassian.com",
            contract_start=date(2023, 6, 1), contract_end=date(2026, 5, 31),
            score=64.3,
        ),
        dict(
            name="Deloitte & Touche Kenya",
            description=(
                "Co-sourced internal audit partner providing IT audit specialists for the "
                "annual audit plan. Prior contract lapsed pending renewal and security review."
            ),
            category="Assurance / Audit",
            website="https://www2.deloitte.com/ke",
            tier=3, status="Under Review",
            contact_name="Deloitte Internal Audit Partner",
            contact_email="internalaudit@deloitte.co.ke",
            contract_start=date(2022, 4, 1), contract_end=date(2026, 3, 31),
            score=52.6,
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
            status="In Remediation",
            owner="Chief Technology Officer",
            due_date=date(2026, 5, 31),
        ),
        # ---- Closed findings: the 4 CBK 2024 examination points already remediated ----
        AuditFinding(
            plan_id=plan.id,
            title="Shared administrator credentials on FLEXCUBE application servers",
            description=(
                "The 2024 CBK examination found shared 'flexadmin' credentials in use across "
                "the FLEXCUBE application tier, preventing attribution of privileged actions. "
                "Closed: individual named accounts issued to all 7 administrators, shared "
                "account disabled, and MFA enforced via Azure AD. Verified by re-test in "
                "the FY2026 assessment."
            ),
            severity="High",
            status="Closed",
            owner="Head of Infrastructure",
            due_date=date(2026, 3, 31),
        ),
        AuditFinding(
            plan_id=plan.id,
            title="No formal information security policy set approved by the Board",
            description=(
                "The 2024 CBK examination found the information security policy suite had not "
                "been reviewed or Board-approved since 2021. Closed: full policy set rewritten "
                "against ISO 27001:2022, approved by the Board Risk Committee in November 2025, "
                "and published to all staff with acknowledgement tracking."
            ),
            severity="Medium",
            status="Closed",
            owner="Chief Information Security Officer",
            due_date=date(2025, 12, 31),
        ),
        AuditFinding(
            plan_id=plan.id,
            title="Absence of network segmentation between SWIFT and office networks",
            description=(
                "The 2024 CBK examination found the SWIFT Alliance Gateway resided on the "
                "general office VLAN, contrary to SWIFT CSP Control 1.1. Closed: dedicated "
                "SWIFT secure zone implemented with firewall enforcement and jump-host access "
                "only. Confirmed during the FY2026 assessment."
            ),
            severity="High",
            status="Closed",
            owner="Head of Infrastructure",
            due_date=date(2026, 1, 31),
        ),
        AuditFinding(
            plan_id=plan.id,
            title="Security awareness training not completed by all staff",
            description=(
                "The 2024 CBK examination found security awareness completion at 61% against "
                "a policy target of 95%. Closed: training moved into onboarding and made an "
                "annual mandatory module with line-manager escalation. Completion reached "
                "97.2% (240/247 staff) at the April 2026 checkpoint."
            ),
            severity="Medium",
            status="Closed",
            owner="Head of Human Resources",
            due_date=date(2026, 4, 30),
        ),
    ]
    for finding in findings:
        session.add(finding)

    await session.flush()

    # ------------------------------------------------------------------
    # 6. Statement of Applicability + SOC 2 readiness (WBS 1.5.2, 1.5.3)
    # ------------------------------------------------------------------
    await _seed_soa(session)

    await session.commit()
    logger.info("Savanna Commercial Bank demo data seeded successfully")


# ---------------------------------------------------------------------------
# Statement of Applicability
# ---------------------------------------------------------------------------

# ISO 27001 controls whose position differs from the certified-baseline default.
# Savanna holds an ISO 27001:2022 certificate (awarded October 2025), so the
# default position is Implemented; these are the controls where open risks and
# audit findings say otherwise. Each justification ties back to a specific risk
# or finding elsewhere in this seed.
_ISO_OVERRIDES = {
    "5.2": ("Partially Implemented",
            "Security roles are defined, but Board-level IT risk reporting lacks quantified "
            "metrics and appetite thresholds (open CBK 2024 examination finding). "
            "Quarterly Board dashboard designed; first submission June 2026.",
            "Chief Information Security Officer"),
    "5.4": ("Partially Implemented",
            "Management direction is documented, but reconciliation break approvals and "
            "Board IT risk oversight are not yet evidenced to the standard the CBK expects.",
            "Head of Compliance"),
    "5.7": ("Planned",
            "Threat intelligence consumption is ad hoc. A MISP feed integration has been "
            "implemented in the GRC platform but is not yet operationalised into the "
            "risk assessment cycle.",
            "Chief Information Security Officer"),
    "5.18": ("Partially Implemented",
             "Access rights are reviewed quarterly for FLEXCUBE, but the SWIFT Alliance "
             "Gateway still uses shared administrator credentials. PAW deployment and "
             "named accounts due 30 June 2026.",
             "Chief Information Security Officer"),
    "5.19": ("Partially Implemented",
             "Supplier relationships are governed by contract, but InfoMark Kenya "
             "subcontracts ATM maintenance to engineers who have not been screened by "
             "the bank. Contract variation issued.",
             "Head of Operations"),
    "5.20": ("Partially Implemented",
             "Security requirements are included in new agreements. Several legacy "
             "contracts, including InfoMark (expired March 2026), predate the current "
             "clause set and are being renegotiated.",
             "Head of Compliance"),
    "5.22": ("Partially Implemented",
             "Supplier performance is reviewed annually. Fourth-party sub-processors used "
             "by Craft Silicon for push notifications and analytics remain undisclosed; "
             "a full sub-processor register has been requested.",
             "Data Protection Officer"),
    "5.23": ("Partially Implemented",
             "Azure Policy denies anonymous blob access tenant-wide and Defender for Cloud "
             "monitoring is enabled, but a formal cloud security baseline standard has not "
             "yet been ratified.",
             "Chief Information Security Officer"),
    "6.7": (None,  # excluded
            "Excluded. Remote access to in-scope systems (FLEXCUBE, SWIFT, the M-Pesa "
            "integration layer) is prohibited by policy; all processing is performed from "
            "bank premises over managed networks. This exclusion is reviewed annually and "
            "will be reversed if remote working is introduced.",
            "Chief Information Security Officer"),
    "7.2": ("Partially Implemented",
            "Badge-controlled entry is live at 9 of 15 branches. The remaining 6 rely on a "
            "shared mechanical key with a manual sign-out register; rollout completes Q4 2026.",
            "Head of Operations"),
    "7.3": ("Partially Implemented",
            "Branch server rooms at 6 sites are not yet badge-controlled and produce no "
            "access log, so entry cannot be reconstructed after an incident.",
            "Head of Operations"),
    "8.2": ("Partially Implemented",
            "Privileged access is individually named and MFA-enforced on FLEXCUBE following "
            "closure of the 2024 CBK finding. The SWIFT gateway remains outstanding.",
            "Head of Infrastructure"),
    "8.8": ("Partially Implemented",
            "Authenticated scanning covers all external assets and a monthly patch window is "
            "in place, but the 7-day critical remediation SLA was breached in April 2026 "
            "(CVE-2026-11423 open 22 days). Open audit finding.",
            "Head of Infrastructure"),
    "8.15": ("Partially Implemented",
             "FLEXCUBE, the M-Pesa integration layer, and Azure AD forward to Sentinel. "
             "ATM controllers and branch file servers do not yet log centrally.",
             "Chief Information Security Officer"),
    "8.16": ("Partially Implemented",
             "SIEM correlation rules cover payments and authentication. Branch-level activity "
             "is outside monitoring coverage, and AML alert thresholds are still being tuned.",
             "Chief Information Security Officer"),
    "8.24": ("Partially Implemented",
             "TLS and HSM-backed key management are in place for card and payment flows. "
             "Three upcountry branch WAN links still carry unencrypted internal traffic "
             "pending IPSec rollout.",
             "Head of Infrastructure"),
    "8.28": ("Planned",
             "Secure coding standards apply to the in-house integration layer but have not "
             "been contractually imposed on Craft Silicon. Scheduled for the 2026 contract "
             "renewal.",
             "Chief Technology Officer"),
    "8.34": ("Planned",
             "Audit testing of production systems is coordinated informally. A formal "
             "protection procedure is drafted and awaiting approval.",
             "Head of Internal Audit"),
}

# SOC 2 Common Criteria assessed so far. Savanna is not pursuing SOC 2
# certification (it is on the ISO 27001 track); this is the assurance posture it
# presents to digital-channel and API partners, per CHG-012. Deliberately
# partial — the unassessed criteria show the SoA as a live document.
_SOC2_ASSESSED = {
    "CC1.1": ("Implemented", "Code of conduct and ethics policy approved by the Board; annual staff attestation at 97.2%.", "Head of Human Resources"),
    "CC1.2": ("Implemented", "Board Risk Committee provides independent oversight of the security programme; charter reviewed 2025.", "Chief Executive Officer"),
    "CC1.3": ("Implemented", "Organisational structure, reporting lines, and security authorities documented in the ISMS manual.", "Chief Information Security Officer"),
    "CC1.4": ("Partially Implemented", "Competence requirements defined for security roles; the second FLEXCUBE DBA post is unfilled until July 2026.", "Head of Human Resources"),
    "CC1.5": ("Implemented", "Individual performance objectives include security accountability for all managers.", "Head of Human Resources"),
    "CC2.1": ("Implemented", "Security metrics and risk information flow to the Board Risk Committee quarterly.", "Chief Information Security Officer"),
    "CC2.2": ("Implemented", "Security policies published to all staff with acknowledgement tracking; awareness training mandatory and annual.", "Chief Information Security Officer"),
    "CC2.3": ("Partially Implemented", "Customer-facing security commitments are published, but partner-facing communication is handled case by case.", "Head of Digital Banking"),
    "CC3.1": ("Implemented", "Risk objectives defined in the ISMS scope; risk register maintained in the GRC platform.", "Chief Information Security Officer"),
    "CC3.2": ("Implemented", "25 risks identified and assessed with impact, likelihood, and residual scoring.", "Chief Information Security Officer"),
    "CC3.3": ("Partially Implemented", "Fraud risk is assessed for insider RTGS transfers and agency banking, but no consolidated fraud risk assessment exists.", "Head of Compliance"),
    "CC3.4": ("Partially Implemented", "Change to the M-Pesa and mobile banking estate is assessed, but change-driven risk reassessment is not consistently evidenced.", "Chief Technology Officer"),
    "CC4.1": ("Implemented", "Internal audit plan executed with Deloitte co-source; FY2026 assessment covers all in-scope systems.", "Head of Internal Audit"),
    "CC4.2": ("Implemented", "Findings tracked to closure with owners and due dates; 4 of the 2024 CBK findings closed.", "Chief Information Security Officer"),
    "CC5.1": ("Implemented", "Control activities selected against ISO 27001:2022 Annex A and documented in the SoA.", "Chief Information Security Officer"),
    "CC5.2": ("Partially Implemented", "Technology controls are largely automated; branch physical controls remain partly manual.", "Head of Operations"),
    "CC5.3": ("Implemented", "Policies and procedures deployed with named owners and review cycles.", "Chief Information Security Officer"),
    "CC6.1": ("Partially Implemented", "Logical access is role-based and MFA-enforced except on the SWIFT Alliance Gateway.", "Head of Infrastructure"),
    "CC6.2": ("Implemented", "User registration and de-registration follow a documented joiner/mover/leaver process.", "Head of Human Resources"),
    "CC6.3": ("Partially Implemented", "Quarterly access reviews cover FLEXCUBE; branch file server permissions are not yet in scope.", "Head of Infrastructure"),
    "CC6.6": ("Partially Implemented", "Perimeter controls and WAF are in place; three branch links await IPSec encryption.", "Head of Infrastructure"),
    "CC6.7": ("Implemented", "Data in transit is encrypted for all customer-facing channels; HSMs protect PIN and key material.", "Head of Infrastructure"),
    "CC6.8": ("Implemented", "CrowdStrike Falcon deployed on 98.4% of managed endpoints with central alerting.", "Chief Information Security Officer"),
    "CC7.1": ("Partially Implemented", "Vulnerability scanning is continuous, but remediation SLAs were breached in April 2026.", "Head of Infrastructure"),
    "CC7.2": ("Partially Implemented", "Sentinel monitors core systems; ATM and branch estate are outside coverage.", "Chief Information Security Officer"),
    "CC7.3": ("Implemented", "Security incident response plan tested; CBK notification template prepared.", "Chief Information Security Officer"),
    "CC7.4": ("Implemented", "Incidents triaged, contained, and reported per the incident management procedure.", "Chief Information Security Officer"),
    "CC7.5": ("Implemented", "Recovery procedures tested via the Q4 2025 DR switchover (RTO 3h42m against a 4h target).", "Chief Technology Officer"),
    "CC8.1": ("Partially Implemented", "Change management operates through Jira with CAB approval; emergency change evidence is inconsistent.", "Chief Technology Officer"),
    "CC9.1": ("Implemented", "Business continuity plan maintained with annual DR activation from the Upper Hill site.", "Chief Technology Officer"),
    "CC9.2": ("Partially Implemented", "Vendor due diligence is tiered and scored, but fourth-party visibility is incomplete.", "Head of Compliance"),
}


async def _seed_soa(session: AsyncSession) -> None:
    """Seed the Statement of Applicability for ISO 27001 and SOC 2.

    ISO: every Annex A control gets a position (ISO requires the SoA to account
    for all of them). The default is Implemented, reflecting the October 2025
    certificate; _ISO_OVERRIDES carries the exceptions.

    SOC 2: only the criteria in _SOC2_ASSESSED are given a position, leaving the
    rest genuinely unassessed.
    """
    frameworks = {
        f.slug: f
        for f in (await session.execute(select(Framework))).scalars().all()
    }

    iso = frameworks.get("iso27001")
    if iso:
        controls = (await session.execute(
            select(Control).where(Control.framework_id == iso.id)
        )).scalars().all()
        for c in controls:
            override = _ISO_OVERRIDES.get(c.ref)
            if override:
                status, justification, owner = override
                if status is None:  # excluded from scope
                    session.add(_soa(c.id, False, "Not Implemented", justification, owner))
                else:
                    session.add(_soa(c.id, True, status, justification, owner))
            else:
                session.add(_soa(
                    c.id, True, "Implemented",
                    "Implemented and evidenced during the BSI Stage 2 certification audit "
                    "(October 2025); no non-conformity raised at the most recent "
                    "surveillance audit.",
                    "Chief Information Security Officer",
                ))
        logger.info("Seeded ISO 27001 SoA: %d controls", len(controls))

    soc2 = frameworks.get("soc2")
    if soc2:
        controls = (await session.execute(
            select(Control).where(Control.framework_id == soc2.id)
        )).scalars().all()
        seeded = 0
        for c in controls:
            assessed = _SOC2_ASSESSED.get(c.ref)
            if not assessed:
                continue
            status, justification, owner = assessed
            session.add(_soa(c.id, True, status, justification, owner))
            seeded += 1
        logger.info("Seeded SOC 2 readiness: %d criteria assessed", seeded)
