"""
Framework seeder — loads YAML files from backend/frameworks/ into the database.
Idempotent: skips any framework whose slug already exists.
"""
import logging
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.control import Control, Framework

logger = logging.getLogger(__name__)

FRAMEWORKS_DIR = Path(__file__).parent.parent / "frameworks"


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
