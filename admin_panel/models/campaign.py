from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_panel.models.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String, nullable=False)
    template_id: Mapped[str] = mapped_column(ForeignKey("templates.id"), nullable=False)

    template: Mapped["MessageTemplate"] = relationship(back_populates="campaigns")
    recipients: Mapped[list["Recipient"]] = relationship(
        secondary="campaign_recipients",
        back_populates="campaigns"
    )
    deliveries: Mapped[list["DeliveryHistory"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return f"{self.name}"