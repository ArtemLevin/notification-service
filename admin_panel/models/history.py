from datetime import datetime

from sqlalchemy import Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_panel.models.base import Base, Status, RepeatInterval


class DeliveryHistory(Base):
    __tablename__ = "delivery_history"

    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"))

    status: Mapped[Status] = mapped_column(SQLEnum(Status), default=Status.pending)
    repeat: Mapped[RepeatInterval] = mapped_column(SQLEnum(RepeatInterval), default=RepeatInterval.none)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # связи
    campaign: Mapped["Campaign"] = relationship(back_populates="deliveries")