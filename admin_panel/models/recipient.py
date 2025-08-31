from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_panel.models.base import Base


class Recipient(Base):
    __tablename__ = "recipients"

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    campaigns: Mapped[list["Campaign"]] = relationship(
        secondary="campaign_recipients",
        back_populates="recipients"
    )

    def __str__(self) -> str:
        return f"{self.email}"
