"""
Framework seeder — loads YAML files from backend/frameworks/ into the database.
Idempotent: skips any framework whose slug already exists.

Also seeds the 18 standard TPRM vendor questions (idempotent by ref).
"""
import logging
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.control import Control, Framework
from app.models.tprm import VendorQuestion

logger = logging.getLogger(__name__)

FRAMEWORKS_DIR = Path(__file__).parent.parent / "frameworks"

# 18 standard TPRM questions — keyed by ref for idempotent upsert
VENDOR_QUESTIONS = [
    {
        "ref": "Q01",
        "category": "Data & Privacy",
        "text": "Does the vendor maintain a formal data classification policy covering personal and sensitive data?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 1.5,
    },
    {
        "ref": "Q02",
        "category": "Data & Privacy",
        "text": "Does the vendor operate under a Data Processing Agreement (DPA) or equivalent contractual data protection obligations?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 2.0,
    },
    {
        "ref": "Q03",
        "category": "Data & Privacy",
        "text": "Describe the vendor's data retention and deletion practices, including confirmed timelines for data destruction on contract termination.",
        "question_type": "scored_with_text",
        "max_score": 5,
        "weight": 1.5,
    },
    {
        "ref": "Q04",
        "category": "Security Controls",
        "text": "Does the vendor hold a current ISO 27001, SOC 2 Type II, or equivalent certification? If yes, specify certification type and expiry.",
        "question_type": "scored_with_text",
        "max_score": 10,
        "weight": 2.5,
    },
    {
        "ref": "Q05",
        "category": "Security Controls",
        "text": "Does the vendor enforce multi-factor authentication (MFA) for all administrative and privileged access?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 2.0,
    },
    {
        "ref": "Q06",
        "category": "Security Controls",
        "text": "Does the vendor perform annual penetration testing by an independent third party?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 1.5,
    },
    {
        "ref": "Q07",
        "category": "Security Controls",
        "text": "Does the vendor apply encryption in transit (TLS 1.2+) and at rest (AES-256 or equivalent) for all customer data?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 2.0,
    },
    {
        "ref": "Q08",
        "category": "Security Controls",
        "text": "Describe the vendor's vulnerability management programme, including patch cadence for critical vulnerabilities.",
        "question_type": "scored_with_text",
        "max_score": 5,
        "weight": 1.5,
    },
    {
        "ref": "Q09",
        "category": "Incident Response",
        "text": "Does the vendor maintain a documented Incident Response Plan (IRP) that has been tested within the last 12 months?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 2.0,
    },
    {
        "ref": "Q10",
        "category": "Incident Response",
        "text": "What is the vendor's contractual commitment for notifying customers of a security incident affecting their data (specify hours)?",
        "question_type": "scored_with_text",
        "max_score": 5,
        "weight": 2.0,
    },
    {
        "ref": "Q11",
        "category": "Incident Response",
        "text": "Describe any security incidents (breaches, ransomware, data loss) experienced by the vendor in the last 24 months.",
        "question_type": "free_text",
        "max_score": 0,
        "weight": 0.0,
    },
    {
        "ref": "Q12",
        "category": "Business Continuity",
        "text": "Does the vendor maintain a Business Continuity Plan (BCP) and Disaster Recovery Plan (DRP) with defined RTO and RPO targets?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 1.5,
    },
    {
        "ref": "Q13",
        "category": "Business Continuity",
        "text": "Has the vendor tested its BCP/DRP within the last 12 months? Describe the test type and outcome.",
        "question_type": "scored_with_text",
        "max_score": 5,
        "weight": 1.5,
    },
    {
        "ref": "Q14",
        "category": "Sub-processor & Supply Chain",
        "text": "Does the vendor maintain an up-to-date register of sub-processors or fourth-party suppliers that have access to customer data?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 1.5,
    },
    {
        "ref": "Q15",
        "category": "Sub-processor & Supply Chain",
        "text": "Does the vendor impose equivalent security and data protection obligations on its sub-processors via contract?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 1.5,
    },
    {
        "ref": "Q16",
        "category": "Contractual & Compliance",
        "text": "Does the vendor's contract include an explicit right-to-audit clause?",
        "question_type": "scored",
        "max_score": 5,
        "weight": 1.0,
    },
    {
        "ref": "Q17",
        "category": "Contractual & Compliance",
        "text": "Does the vendor maintain compliance with applicable data protection regulations (e.g. GDPR, CCPA)? Specify applicable laws.",
        "question_type": "scored_with_text",
        "max_score": 5,
        "weight": 2.0,
    },
    {
        "ref": "Q18",
        "category": "Contractual & Compliance",
        "text": "Are there any current or pending regulatory investigations, litigation, or material compliance failures relating to data protection or security?",
        "question_type": "free_text",
        "max_score": 0,
        "weight": 0.0,
    },
]


async def seed_frameworks(session: AsyncSession) -> None:
    if not FRAMEWORKS_DIR.exists():
        logger.warning("frameworks/ directory not found at %s — skipping seed", FRAMEWORKS_DIR)
        return

    for yaml_file in sorted(FRAMEWORKS_DIR.glob("*.yaml")):
        data = yaml.safe_load(yaml_file.read_text())
        slug = data["slug"]

        result = await session.execute(select(Framework).where(Framework.slug == slug))
        if result.scalar_one_or_none():
            logger.debug("Framework %r already present — skipping", slug)
            continue

        framework = Framework(
            slug=slug,
            name=data["name"],
            version=data["version"],
            description=data.get("description"),
        )
        session.add(framework)
        await session.flush()  # get framework.id before inserting controls

        for ctrl in data.get("controls", []):
            session.add(
                Control(
                    framework_id=framework.id,
                    ref=ctrl["ref"],
                    domain=ctrl["domain"],
                    title=ctrl["title"],
                    description=ctrl.get("description"),
                )
            )

        logger.info("Seeded framework %r (%d controls)", slug, len(data.get("controls", [])))

    await session.commit()


async def seed_vendor_questions(session: AsyncSession) -> None:
    """Idempotently seed the 18 standard TPRM vendor questions."""
    for q_data in VENDOR_QUESTIONS:
        result = await session.execute(
            select(VendorQuestion).where(VendorQuestion.ref == q_data["ref"])
        )
        if result.scalar_one_or_none():
            logger.debug("Vendor question %r already present — skipping", q_data["ref"])
            continue

        question = VendorQuestion(
            ref=q_data["ref"],
            category=q_data["category"],
            text=q_data["text"],
            question_type=q_data["question_type"],
            max_score=q_data["max_score"],
            weight=q_data["weight"],
        )
        session.add(question)

    await session.commit()
    logger.info("Vendor question seeding complete")
