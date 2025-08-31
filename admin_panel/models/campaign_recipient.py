from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from admin_panel.models.base import Base


class CampaignRecipient(Base):
    __tablename__ = "campaign_recipients"
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), primary_key=True)
    recipient_id: Mapped[str] = mapped_column(ForeignKey("recipients.id"), primary_key=True)
