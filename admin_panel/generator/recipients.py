from faker import Faker
from admin_panel.core.db import AsyncDBSession
from sqlalchemy import select

from admin_panel.models.recipient import Recipient

fake = Faker("ru_RU")


async def init_recipients(count: int = 20):
    async with AsyncDBSession() as session:
        res = await session.execute(select(Recipient))
        if res.scalars().first():
            return

        for _ in range(count):
            profile = fake.simple_profile()

            session.add(Recipient(
                name=profile["name"],
                email=profile["mail"],
            ))

        await session.commit()

